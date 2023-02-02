from whylabs_toolkit.monitor.models import Monitor, Analyzer


class MonitorBuilder:
    def __init__(self) -> None:
        self.analyzer = None
        self.monitor = None

    def create_analyzer_schedule(self):
        pass
    
    def create_analyzer_target(self):
        pass
    
    def create_analyzer_config(self):
        pass
    
    def create_analyzer(self) -> None:
        self.analyzer: Analyzer = Analyzer()
        self.create_analyzer_schedule()
        self.create_analyzer_target()
        self.create_analyzer_config()
    
    
    def create_monitor_severity(self):
        pass
    
    def create_monitor_mode(self):
        # digest or everyAnomaly
        # filter out anomalies
        pass
    
    def create_monitor_actions(self):
        # slack, email, globalAction
        pass
     
    def create_monitor(self) -> None:
        self.monitor: Monitor = Monitor()
        self.create_monitor_severity()
        self.create_monitor_actions()
        self.create_monitor_mode()


