"""Resource management for Isolator."""
import os
import logging
from dataclasses import dataclass
from typing import List, Optional, Dict
from pathlib import Path

@dataclass
class ResourceLimits:
    """Resource limits configuration."""
    memory_limit: Optional[str] = None  # e.g., "2G"
    cpu_limit: Optional[int] = None     # percentage
    io_weight: Optional[int] = None     # 10-1000
    max_processes: Optional[int] = None  # max number of processes
    max_file_size: Optional[str] = None # e.g., "1G"
    max_files: Optional[int] = None     # max number of open files

class ResourceManager:
    """Manages system resources and limits for isolated applications."""
    
    def __init__(self, limits: Optional[ResourceLimits] = None):
        self.limits = limits or ResourceLimits()
        self.logger = logging.getLogger(__name__)
        self.cgroup_root = Path("/sys/fs/cgroup")
        self._validate_cgroup_support()

    def _validate_cgroup_support(self):
        """Validate cgroup support on the system."""
        if not self.cgroup_root.exists():
            self.logger.warning("Cgroup filesystem not found, resource limits may not work")
            return False
            
        # Check cgroup version
        if (self.cgroup_root / "cgroup.controllers").exists():
            self.cgroup_version = 2
        else:
            self.cgroup_version = 1
            
        return True

    def get_resource_args(self) -> List[str]:
        """Get bubblewrap arguments for resource management."""
        args = []
        
        # Basic resource limits
        if self.limits.max_processes:
            args.extend(["--rlimit", f"nproc={self.limits.max_processes}"])
            
        if self.limits.max_files:
            args.extend(["--rlimit", f"nofile={self.limits.max_files}"])
            
        if self.limits.max_file_size:
            size_bytes = self._parse_size(self.limits.max_file_size)
            args.extend(["--rlimit", f"fsize={size_bytes}"])
            
        # Memory limits
        if self.limits.memory_limit:
            mem_bytes = self._parse_size(self.limits.memory_limit)
            args.extend(["--rlimit", f"as={mem_bytes}"])
            
        # Setup cgroup if available
        cgroup_args = self._setup_cgroup()
        if cgroup_args:
            args.extend(cgroup_args)
            
        return args

    def _setup_cgroup(self) -> List[str]:
        """Setup cgroup constraints."""
        args = []
        
        if self.cgroup_version == 2:
            # Use cgroup v2
            if self.limits.cpu_limit:
                args.extend([
                    "--bind-data", f"{self.limits.cpu_limit}",
                    "/sys/fs/cgroup/cpu.max"
                ])
                
            if self.limits.memory_limit:
                mem_bytes = self._parse_size(self.limits.memory_limit)
                args.extend([
                    "--bind-data", f"{mem_bytes}",
                    "/sys/fs/cgroup/memory.max"
                ])
                
            if self.limits.io_weight:
                args.extend([
                    "--bind-data", f"{self.limits.io_weight}",
                    "/sys/fs/cgroup/io.weight"
                ])
        else:
            # Use cgroup v1
            if self.limits.cpu_limit:
                args.extend([
                    "--bind-data", f"{self.limits.cpu_limit * 1000}",
                    "/sys/fs/cgroup/cpu/cpu.cfs_quota_us"
                ])
                
            if self.limits.memory_limit:
                mem_bytes = self._parse_size(self.limits.memory_limit)
                args.extend([
                    "--bind-data", f"{mem_bytes}",
                    "/sys/fs/cgroup/memory/memory.limit_in_bytes"
                ])
                
        return args

    def _parse_size(self, size_str: str) -> int:
        """Parse size string (e.g., '2G', '500M') to bytes."""
        units = {
            'B': 1,
            'K': 1024,
            'M': 1024 * 1024,
            'G': 1024 * 1024 * 1024,
            'T': 1024 * 1024 * 1024 * 1024
        }
        
        size = size_str.strip()
        unit = size[-1].upper()
        if unit not in units:
            raise ValueError(f"Invalid size unit in {size_str}")
            
        try:
            number = float(size[:-1])
            return int(number * units[unit])
        except ValueError:
            raise ValueError(f"Invalid size format: {size_str}")

    def monitor_resources(self) -> Dict[str, any]:
        """Monitor current resource usage."""
        usage = {}
        
        try:
            # Memory usage
            with open("/proc/self/status") as f:
                for line in f:
                    if line.startswith("VmRSS:"):
                        usage["memory_rss"] = int(line.split()[1]) * 1024
                        break
                        
            # CPU usage (requires psutil)
            import psutil
            process = psutil.Process()
            usage["cpu_percent"] = process.cpu_percent()
            usage["num_threads"] = process.num_threads()
            usage["open_files"] = len(process.open_files())
            
        except Exception as e:
            self.logger.warning(f"Failed to monitor resources: {e}")
            
        return usage

    def cleanup(self):
        """Clean up any resource management related state."""
        # Remove cgroup if we created one
        try:
            if hasattr(self, 'cgroup_path') and self.cgroup_path.exists():
                self.cgroup_path.rmdir()
        except Exception as e:
            self.logger.warning(f"Failed to clean up cgroup: {e}")
