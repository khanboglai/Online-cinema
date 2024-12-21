import logging
from enum import Enum
from datetime import datetime
from typing import Any, List, Tuple
from abc import ABC, abstractmethod

class StageOut:
    """
    Stage output wrapper unified object
    """

    def __init__(self, obj: Any):
        self._object: Any = obj
    
    def unpack(self) -> Any:
        """Unpacks object from wrapper"""
        
        return self._object

class StageABC(ABC):
    """
    Pipeline stage abstract base class
    """

    def __init__(self, name: str = "stage") -> None:
        self._name = name

    @abstractmethod
    def run(self, input: StageOut | None = None) -> StageOut:
        """Run pipeline stage"""
        ...

class PipelineMsg(Enum):
    INFO = 0
    ERROR = 1

class Pipeline:
    """
    Simple pipeline
    """

    def __init__(self, stages: List[StageABC], logger: logging.Logger | None) -> None:
        if len(stages) == 0:
            raise ValueError("Empty pipeline is not allowed")

        self._stages = stages
        self._logger = logger

    def run_all(self) -> Tuple[bool, int]:
        """Runs all pipeline stages"""

        out = None
        for n, stage in enumerate(self._stages, 1):
            try:
                self._log(f"Starting stage <{stage._name}> #{n}...")
                out = stage.run(out)
                self._log(f"Stage <{stage._name}> #{n} finished successfully")
            except Exception as e:
                if self._logger is not None:
                    self._log(f"Pipeline failed at stage <{stage._name}> #{n}: {e}", PipelineMsg.ERROR)
                return (False, n)
        return (True, 0)
    
    def get_logger(self) -> logging.Logger | None:
        """Returns the associated logger"""

        return self._logger

    def _log(self, msg: str, type: PipelineMsg = PipelineMsg.INFO) -> None:
        if self._logger is None:
            return
        
        match(type):
            case PipelineMsg.INFO:
                self._logger.info(f"[{datetime.now()}][INFO]: {msg}")
            case PipelineMsg.ERROR:
                self._logger.info(f"[{datetime.now()}][ERROR]: {msg}")
