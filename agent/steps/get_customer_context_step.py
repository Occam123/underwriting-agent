from typing import Dict, Any
from model.pipeline import Step
from model.messageQueue.instance import message_queue
from agent.AgentContext import agent_ctx

from service.CustomerService import customer_service
from agent.actions import init_customer
from service.CustomerService import customer_service

async def get_customer_context(step_ctx: Dict[str, Any]):
    customer_name = step_ctx["find_customer_step"]["customer_name"]
    customer_ctx = agent_ctx.get(customer_name)
    if customer_ctx is None:
        default_ctx = {
            "submissions": []
        }
        agent_ctx[customer_name] = default_ctx
        customer = await customer_service.create_customer(customer_name)
        customer_id = customer.id
        return {
            "new": True,
            "customer_name": customer_name,
            "customer_ctx": default_ctx,
            "customer_id": customer_id
        }
    return {
        "new": False,
        "customer_name": customer_name,
        "customer_ctx": customer_ctx,
        "customer_id": customer_id
    }


def get_customer_context_step():
    def start_message(step_ctx):
        return f"I am checking if {step_ctx['find_customer_step']['customer_name']} has an existing case in the system."

    def end_message(step_result, _):
        if step_result["new"]:
            return (
                f"No existing submission found for {step_result['customer_name']}. I have created a new submission."
            )
        else:
            return (
                f"A case already exists for {step_result['customer_name']}."
            )

    return Step(
        id="get_customer_context_step",
        name="Get Customer Context Step",
        function=get_customer_context,
        start_message=start_message,
        end_message=end_message,
        message_queue=message_queue
    )
