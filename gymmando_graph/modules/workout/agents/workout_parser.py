from pathlib import Path
from typing import cast

from dotenv import load_dotenv
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain_openai import ChatOpenAI

from gymmando_graph.modules.workout.schemas import WorkoutParserResponse
from gymmando_graph.utils import PromptTemplateLoader

load_dotenv()


class WorkoutParser:
    def __init__(self):
        # define the parser
        self.parser = PydanticOutputParser(pydantic_object=WorkoutParserResponse)
        format_instructions = self.parser.get_format_instructions()

        # initialize the prompt
        # Get the prompt templates directory relative to this file
        prompts_dir = Path(__file__).parent.parent / "prompt_templates"
        ptl = PromptTemplateLoader(str(prompts_dir))
        system_template = ptl.load_template("workout_parser_prompt_template_system.md")
        human_template = ptl.load_template("workout_parser_prompt_template_human.md")
        system_message = SystemMessagePromptTemplate.from_template(
            template=system_template
        )
        human_message = HumanMessagePromptTemplate.from_template(
            template=human_template, input_variables=["user_input"]
        )

        self.prompt = ChatPromptTemplate.from_messages(
            [system_message, human_message]
        ).partial(format_instructions=format_instructions)

        # initialize the LLM (OpenAI)
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0,
        )

        # create the chain
        self.chain = self.prompt | self.llm | self.parser

    def show_prompt(self, user_input: str):
        return self.prompt.format(user_input=user_input)

    def process(self, user_input: str) -> WorkoutParserResponse:
        """Process user input through the LLM chain and return parsed response."""
        response = self.chain.invoke({"user_input": user_input})
        return cast(WorkoutParserResponse, response)


if __name__ == "__main__":
    parser = WorkoutParser()
    result = parser.process("Squats 20 reps, 3 sets and for 20 minutes?")
    print(result.model_dump_json(indent=2))
