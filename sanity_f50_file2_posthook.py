from senti_core_module.senti_core.execution.execution_engine import ExecutionEngine
from senti_core_module.senti_core.execution.execution_hooks import ExecutionLifecycleHooks


class FailingPostHook(ExecutionLifecycleHooks):
    def pre_execute(self, context, budget):
        pass

    def post_execute(self, context, budget, result):
        raise RuntimeError("post hook boom")


class OkResolver:
    def resolve(self, context):
        return lambda *, context: "OK"


engine = ExecutionEngine(
    executor_resolver=OkResolver(),
    hooks=FailingPostHook(),
)

rep = engine.execute({}, {})

assert rep.result.status.value == "failed"
assert "post_execute hook failed" in rep.result.error

print("FAZA 50 FILE 2/? POST-HOOK FAILURE PASS")
