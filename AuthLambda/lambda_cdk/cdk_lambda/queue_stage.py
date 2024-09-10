from constructs import Construct
from aws_cdk import(
    aws_lambda_event_sources as lambda_event_sources,
    aws_sqs as sqs,
    Stack,
    Duration,
    Stage,
)

class QueueStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        self.queue = sqs.Queue(
            self,
            "TestSQSQueue",
            visibility_timeout=Duration.seconds(300)
        )
        
        # event source
        self.sqs_event_source = lambda_event_sources.SqsEventSource(self.queue)
        
        #   # add event source
        # _lambda.add_event_source(sqs_event_source)
        
class QueueStage(Stage):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        self.stack = QueueStack(self, "queue-stack", **kwargs)