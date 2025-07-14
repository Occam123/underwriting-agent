from typing import Optional
from model.Email import Email
from model.pipeline import Step
from llm.instance import llm
from llm.OpenAi import Model
from helpers import read_system_prompt
from model.schemas.Basic import StringValue
from model.messageQueue.instance import message_queue
from agent.AgentContext import agent_ctx


def find_customer_based_on_email_content(email: Email) -> Optional[str]:
    context = f"============== Email ==============\n{email.dump()}"
    result = llm.chat(
        message=f"============== Context ==============\n{context}",
        system_message=read_system_prompt("id_customer.md"),
        model=Model.o4_mini,
        response_format=StringValue,
        reasoning={
            "effort": "medium",
            "summary": "detailed"
        }
    )
    return {
        "result": result["result"].model_dump()["value"] if result["result"] else None,
        "summary": result.get("summary")
    }


def find_customer_based_on_email_chain(email: Email) -> Optional[str]:
    previous_email_id = email.previous_email_id
    for customer_name, submissions in agent_ctx.items():
        for submission in submissions:
            email_chain = submission.get("email_chain", [])
            email_chain_ids = [email.id for email in email_chain]
            if previous_email_id in email_chain_ids:
                return customer_name
    return None


def find_customer(email: Email) -> Optional[str]:
    customer_name = find_customer_based_on_email_chain(email)
    if customer_name is not None:
        return customer_name

    result = find_customer_based_on_email_content(email)
    customer_name = result["result"]
    return customer_name


def find_customer_step(email: Email):
    def start_message(_):
        return "I am analyzing the email to identify the associated customer or organization."

    def end_message(step_result, _):
        name = step_result["customer_name"]
        if name:
            return f"The customer associated with this inquiry is: {name}."
        else:
            return "I could not confidently assign a customer to this inquiry."

    return Step(
        id="find_customer_step",
        name="Find Customer Step",
        function=lambda _: {
            "customer_name": find_customer(email)
        },
        start_message=start_message,
        end_message=end_message,
        message_queue=message_queue
    )
