"""
System Initializer Component
============================

Handles initialization of all core systems for the main window.
Extracted from main_window.py for better modularity and maintainability.
"""

import logging
import asyncio
from typing import Dict, Any, Optional
from pathlib import Path

from PyQt6.QtCore import QObject, pyqtSignal

# Import core systems
from dreamscape.core.memory import MemoryManager
from dreamscape.core.mmorpg.mmorpg_engine import MMORPGEngine
from dreamscape.core.legacy.resume_tracker import ResumeTracker
from dreamscape.core.mmorpg.enhanced_skill_resume_system import EnhancedSkillResumeSystem
from dreamscape.core.discord import DiscordManager
from dreamscape.core.scraping_system import ScraperOrchestrator
from dreamscape.core.dreamscape_processor import DreamscapeProcessor
from dreamscape.core.templates.prompt_deployer import PromptDeployer
from dreamscape.core.settings_manager import settings_manager

logger = logging.getLogger(__name__)


class SystemInitializer(QObject):
    """
    Handles initialization of all core systems for the main window.
    
    This component is responsible for:
    - Initializing all core system managers
    - Validating system dependencies
    - Setting up system connections
    - Providing system status information
    """
    
    # Signals
    systems_initialized = pyqtSignal(dict)  # Emitted when all systems are initialized
    system_error = pyqtSignal(str, str)     # Emitted when a system fails to initialize
    initialization_progress = pyqtSignal(int, str)  # Progress updates during initialization
    
    def __init__(self):
        super().__init__()
        
        # Core system managers
        self.memory_manager: Optional[MemoryManager] = None
        self.mmorpg_engine: Optional[MMORPGEngine] = None
        self.discord_manager: Optional[DiscordManager] = None
        self.scraping_manager: Optional[ScraperOrchestrator] = None
        self.resume_tracker: Optional[ResumeTracker] = None
        self.enhanced_skill_system: Optional[EnhancedSkillResumeSystem] = None
        self.dreamscape_processor: Optional[DreamscapeProcessor] = None
        self.prompt_deployer: Optional[PromptDeployer] = None
        
        # Initialization status
        self._initialization_status: Dict[str, bool] = {}
        self._initialization_errors: Dict[str, str] = {}
        self._is_initialized = False
    
    def initialize_systems(self) -> Dict[str, Any]:
        """
        Initialize all core systems.
        
        Returns:
            Dictionary containing initialization results and system references
        """
        try:
            logger.info("🚀 Starting system initialization...")
            self.initialization_progress.emit(0, "Starting system initialization...")
            
            # Step 1: Initialize Memory Manager
            self.initialization_progress.emit(10, "Initializing Memory Manager...")
            self._initialize_memory_manager()
            
            # Step 2: Initialize MMORPG Engine
            self.initialization_progress.emit(20, "Initializing MMORPG Engine...")
            self._initialize_mmorpg_engine()
            
            # Step 3: Initialize Resume Tracker
            self.initialization_progress.emit(30, "Initializing Resume Tracker...")
            self._initialize_resume_tracker()
            
            # Step 4: Initialize Enhanced Skill System
            self.initialization_progress.emit(40, "Initializing Enhanced Skill System...")
            self._initialize_enhanced_skill_system()
            
            # Step 5: Initialize Discord Manager
            self.initialization_progress.emit(50, "Initializing Discord Manager...")
            self._initialize_discord_manager()
            
            # Step 6: Initialize Scraping Manager
            self.initialization_progress.emit(60, "Initializing Scraping Manager...")
            self._initialize_scraping_manager()
            
            # Step 7: Initialize Dreamscape Processor
            self.initialization_progress.emit(70, "Initializing Dreamscape Processor...")
            self._initialize_dreamscape_processor()
            
            # Step 8: Initialize Prompt Deployer
            self.initialization_progress.emit(80, "Initializing Prompt Deployer...")
            self._initialize_prompt_deployer()
            
            # Step 9: Setup system connections
            self.initialization_progress.emit(90, "Setting up system connections...")
            self._setup_system_connections()
            
            # Step 10: Validate systems
            self.initialization_progress.emit(95, "Validating systems...")
            self._validate_systems()
            
            # Complete initialization
            self.initialization_progress.emit(100, "System initialization completed!")
            self._is_initialized = True
            
            # Emit completion signal
            systems_data = self._get_systems_data()
            self.systems_initialized.emit(systems_data)
            
            logger.info("✅ System initialization completed successfully")
            return systems_data
            
        except Exception as e:
            error_msg = f"System initialization failed: {str(e)}"
            logger.error(f"❌ {error_msg}")
            self.system_error.emit("initialization", error_msg)
            raise
    
    def _initialize_memory_manager(self):
        """Initialize the Memory Manager."""
        try:
            self.memory_manager = MemoryManager()
            self._initialization_status["memory_manager"] = True
            logger.info("✅ Memory Manager initialized")
        except Exception as e:
            error_msg = f"Memory Manager initialization failed: {str(e)}"
            self._initialization_errors["memory_manager"] = error_msg
            self._initialization_status["memory_manager"] = False
            logger.error(f"❌ {error_msg}")
            self.system_error.emit("memory_manager", error_msg)
    
    def _initialize_mmorpg_engine(self):
        """Initialize the MMORPG Engine."""
        try:
            self.mmorpg_engine = MMORPGEngine()
            self._initialization_status["mmorpg_engine"] = True
            logger.info("✅ MMORPG Engine initialized")
        except Exception as e:
            error_msg = f"MMORPG Engine initialization failed: {str(e)}"
            self._initialization_errors["mmorpg_engine"] = error_msg
            self._initialization_status["mmorpg_engine"] = False
            logger.error(f"❌ {error_msg}")
            self.system_error.emit("mmorpg_engine", error_msg)
    
    def _initialize_resume_tracker(self):
        """Initialize the Resume Tracker."""
        try:
            self.resume_tracker = ResumeTracker()
            self._initialization_status["resume_tracker"] = True
            logger.info("✅ Resume Tracker initialized")
        except Exception as e:
            error_msg = f"Resume Tracker initialization failed: {str(e)}"
            self._initialization_errors["resume_tracker"] = error_msg
            self._initialization_status["resume_tracker"] = False
            logger.error(f"❌ {error_msg}")
            self.system_error.emit("resume_tracker", error_msg)
    
    def _initialize_enhanced_skill_system(self):
        """Initialize the Enhanced Skill Resume System."""
        try:
            self.enhanced_skill_system = EnhancedSkillResumeSystem()
            self._initialization_status["enhanced_skill_system"] = True
            logger.info("✅ Enhanced Skill Resume System initialized")
        except Exception as e:
            error_msg = f"Enhanced Skill Resume System initialization failed: {str(e)}"
            self._initialization_errors["enhanced_skill_system"] = error_msg
            self._initialization_status["enhanced_skill_system"] = False
            logger.error(f"❌ {error_msg}")
            self.system_error.emit("enhanced_skill_system", error_msg)
    
    def _initialize_discord_manager(self):
        """Initialize the Discord Manager."""
        try:
            self.discord_manager = DiscordManager()
            self._initialization_status["discord_manager"] = True
            logger.info("✅ Discord Manager initialized")
        except Exception as e:
            error_msg = f"Discord Manager initialization failed: {str(e)}"
            self._initialization_errors["discord_manager"] = error_msg
            self._initialization_status["discord_manager"] = False
            logger.warning(f"⚠️ {error_msg}")  # Discord is optional, so warning instead of error
            self.system_error.emit("discord_manager", error_msg)
    
    def _initialize_scraping_manager(self):
        """Initialize the Scraping Manager."""
        try:
            self.scraping_manager = ScraperOrchestrator()
            self._initialization_status["scraping_manager"] = True
            logger.info("✅ Scraping Manager initialized")
        except Exception as e:
            error_msg = f"Scraping Manager initialization failed: {str(e)}"
            self._initialization_errors["scraping_manager"] = error_msg
            self._initialization_status["scraping_manager"] = False
            logger.error(f"❌ {error_msg}")
            self.system_error.emit("scraping_manager", error_msg)
    
    def _initialize_dreamscape_processor(self):
        """Initialize the Dreamscape Processor."""
        try:
            self.dreamscape_processor = DreamscapeProcessor()
            self._initialization_status["dreamscape_processor"] = True
            logger.info("✅ Dreamscape Processor initialized")
        except Exception as e:
            error_msg = f"Dreamscape Processor initialization failed: {str(e)}"
            self._initialization_errors["dreamscape_processor"] = error_msg
            self._initialization_status["dreamscape_processor"] = False
            logger.error(f"❌ {error_msg}")
            self.system_error.emit("dreamscape_processor", error_msg)
    
    def _initialize_prompt_deployer(self):
        """Initialize the Prompt Deployer."""
        try:
            self.prompt_deployer = PromptDeployer()
            self._initialization_status["prompt_deployer"] = True
            logger.info("✅ Prompt Deployer initialized")
        except Exception as e:
            error_msg = f"Prompt Deployer initialization failed: {str(e)}"
            self._initialization_errors["prompt_deployer"] = error_msg
            self._initialization_status["prompt_deployer"] = False
            logger.error(f"❌ {error_msg}")
            self.system_error.emit("prompt_deployer", error_msg)
    
    def _setup_system_connections(self):
        """Setup connections between systems."""
        try:
            # Connect MMORPG engine to Discord manager if both are available
            if self.mmorpg_engine and self.discord_manager:
                self.discord_manager.set_mmorpg_engine(self.mmorpg_engine)
                logger.info("✅ Connected MMORPG Engine to Discord Manager")
            
            # Setup other system connections as needed
            logger.info("✅ System connections established")
            
        except Exception as e:
            error_msg = f"System connection setup failed: {str(e)}"
            logger.error(f"❌ {error_msg}")
            self.system_error.emit("connections", error_msg)
    
    def _validate_systems(self):
        """Validate that all critical systems are properly initialized."""
        try:
            critical_systems = [
                "memory_manager",
                "mmorpg_engine", 
                "resume_tracker",
                "enhanced_skill_system",
                "scraping_manager",
                "dreamscape_processor",
                "prompt_deployer"
            ]
            
            failed_systems = []
            for system in critical_systems:
                if not self._initialization_status.get(system, False):
                    failed_systems.append(system)
            
            if failed_systems:
                error_msg = f"Critical systems failed to initialize: {', '.join(failed_systems)}"
                logger.error(f"❌ {error_msg}")
                raise Exception(error_msg)
            
            logger.info("✅ All critical systems validated successfully")
            
        except Exception as e:
            error_msg = f"System validation failed: {str(e)}"
            logger.error(f"❌ {error_msg}")
            self.system_error.emit("validation", error_msg)
            raise
    
    def _get_systems_data(self) -> Dict[str, Any]:
        """Get all system references and status information."""
        return {
            "systems": {
                "memory_manager": self.memory_manager,
                "mmorpg_engine": self.mmorpg_engine,
                "discord_manager": self.discord_manager,
                "scraping_manager": self.scraping_manager,
                "resume_tracker": self.resume_tracker,
                "enhanced_skill_system": self.enhanced_skill_system,
                "dreamscape_processor": self.dreamscape_processor,
                "prompt_deployer": self.prompt_deployer
            },
            "status": self._initialization_status.copy(),
            "errors": self._initialization_errors.copy(),
            "is_initialized": self._is_initialized
        }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get current system status information."""
        return {
            "is_initialized": self._is_initialized,
            "status": self._initialization_status.copy(),
            "errors": self._initialization_errors.copy(),
            "total_systems": len(self._initialization_status),
            "successful_systems": sum(1 for status in self._initialization_status.values() if status),
            "failed_systems": len(self._initialization_errors)
        }
    
    def get_system(self, system_name: str) -> Optional[Any]:
        """Get a specific system by name."""
        systems_map = {
            "memory_manager": self.memory_manager,
            "mmorpg_engine": self.mmorpg_engine,
            "discord_manager": self.discord_manager,
            "scraping_manager": self.scraping_manager,
            "resume_tracker": self.resume_tracker,
            "enhanced_skill_system": self.enhanced_skill_system,
            "dreamscape_processor": self.dreamscape_processor,
            "prompt_deployer": self.prompt_deployer
        }
        return systems_map.get(system_name)
    
    def is_system_available(self, system_name: str) -> bool:
        """Check if a specific system is available."""
        return self._initialization_status.get(system_name, False)
    
    def cleanup_systems(self):
        """Cleanup all systems and resources."""
        try:
            logger.info("🧹 Cleaning up systems...")
            
            # Cleanup systems in reverse order of initialization
            if self.prompt_deployer:
                # Add cleanup logic if needed
                pass
            
            if self.dreamscape_processor:
                # Add cleanup logic if needed
                pass
            
            if self.scraping_manager:
                # Add cleanup logic if needed
                pass
            
            if self.discord_manager:
                # Add cleanup logic if needed
                pass
            
            # Reset status
            self._is_initialized = False
            self._initialization_status.clear()
            self._initialization_errors.clear()
            
            logger.info("✅ Systems cleanup completed")
            
        except Exception as e:
            logger.error(f"❌ Systems cleanup failed: {str(e)}")
            raise 