from app.hooks.agent_hooks import (
    validate_tool_access,
    audit_tool_execution,
)

from app.hooks.hook_manager import hook_manager


hook_manager.register_pre_tool_hook(
    validate_tool_access
)

hook_manager.register_post_tool_hook(
    audit_tool_execution
)