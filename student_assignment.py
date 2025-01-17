import json
from model_configurations import get_model_configuration

from langchain_openai import AzureChatOpenAI
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate, FewShotChatMessagePromptTemplate

from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.prompts.chat import ChatPromptTemplate, MessagesPlaceholder

from langchain.tools import tool
from langchain.agents import  Tool
from langchain.schema import SystemMessage

gpt_chat_version = 'gpt-4o'
gpt_config = get_model_configuration(gpt_chat_version)

def generate_hw01(question):

    llm = AzureChatOpenAI(
        model=gpt_config['model_name'],
        deployment_name=gpt_config['deployment_name'],
        openai_api_key=gpt_config['api_key'],
        openai_api_version=gpt_config['api_version'],
        azure_endpoint=gpt_config['api_base'],
        temperature=gpt_config['temperature']
    )
    message = HumanMessage(
        content=[
            {"type": "text", "text": question},
        ]
    )
    response = llm.invoke([message])
    
    examples = [
        {
            "input": "2024年台灣10月紀念日有哪些?", 
            "output": {
                "Result": [
                    {
                        "date": "2024-10-10",
                        "name": "國慶日"
                    },
                    {
                        "date": "2024-10-11",
                        "name": "重陽節"
                    }
                ]
            }
        }
    ]

    example_prompt = ChatPromptTemplate.from_messages(
        [
            ("human", "{input}"),
            ("ai", "{output}"),
        ]
    )

    few_shot_prompt = FewShotChatMessagePromptTemplate(
        example_prompt=example_prompt,
        examples=examples,
    )
    # print(few_shot_prompt.invoke({}).to_messages())

    final_prompt = ChatPromptTemplate.from_messages(
        [
            ("system",  """你是台灣內政部負責紀念日及節日實施辦法的專業人員,
                            請以JSON格式返回全部符合問題的結果,結果可能很多個,
                            並且去掉了不需要的標記（例如 ```json 和 ```)
                            格式必須包含\"Result\" 
                        """),
            few_shot_prompt,
            ("human", "{input}"),
        ]
    )

    chain = final_prompt | llm
    response_content = chain.invoke({"input": "2024年台灣10月紀念日有哪些"}).content

    print(response_content)

    return response_content

@tool("get_calendar_events")
def get_calendar_events_tool(input: str):
    """
    Fetch calendar events for a specific year and month in Taiwan.
    Input should be in the format 'YYYY-MM'.
    """
    api_key = "6wBgACs2YWxPit5i4YdGNQ30GUybl5kL"
    country = "TW"
    
    year, month = map(int, input.split('-'))
    
    result = call_calendarific_api(api_key, country, year, month)
    return json.dumps(result)

def call_calendarific_api(api_key, country, year, month):
    url = f'https://calendarific.com/api/v2/holidays?api_key={api_key}&country={country}&year={year}&month={month}'
    import requests
    response = requests.get(url)
    if response.status_code != 200:
        raise ValueError(f"API request fail, Status:{response.status_code}")
    
    holidays = response.json().get('response', {}).get('holidays', [])
    
    result = {"Result": [{"date": holiday['date']['iso'], "name": holiday['name']} for holiday in holidays]}
    return result

def generate_hw02(question):
    pass
    # Few-Shot example setup
    examples = [
        {
            "input": "2024年台灣10月紀念日有哪些?",
            "output": {
                "Result": [
                    {"date": "2024-10-10", "name": "國慶日"},
                    {"date": "2024-10-11", "name": "重陽節"}
                ]
            }
        }
    ]
    
    # Few-shot prompt
    few_shot_prompt = FewShotChatMessagePromptTemplate(
        example_prompt=ChatPromptTemplate.from_messages(
            [
                ("human", "{input}"),
                ("ai", "{output}"),
            ]
        ),
        examples=examples,
    )

    # System message that provides instructions
    system_message = SystemMessage(
        content="""你是一位台灣日曆專家，負責回答有關特定月份的台灣節日問題。
        當回答問題時，請務必返回以下格式的 JSON:
        {{
            "Result": [
                {{
                    "date": "YYYY-MM-DD",
                    "name": "節日名稱"
                }},
                ...
            ]
        }}
        僅列出該月份的相關紀念日，其他資訊請不要包含。
        """
    )

    formatted_few_shot_messages = few_shot_prompt.format_messages()

    final_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_message.content),
            MessagesPlaceholder(variable_name="chat_history", optional=True),  # 历史记录占位符
            *formatted_few_shot_messages,  # 插入 Few-shot 示例
            ("human", "{input}"),  # 用户输入
            MessagesPlaceholder(variable_name="agent_scratchpad"),  # 中间步骤占位符
        ]
    )

    # Initialize LLM
    llm = AzureChatOpenAI(
        model=gpt_config['model_name'],
        deployment_name=gpt_config['deployment_name'],
        openai_api_key=gpt_config['api_key'],
        openai_api_version=gpt_config['api_version'],
        azure_endpoint=gpt_config['api_base'],
        temperature=gpt_config['temperature']
    )

    # Define tool
    tools = [
        Tool(
            name="get_calendar_events",
            func=get_calendar_events_tool,
            description="Call this tool to fetch Taiwan's calendar events for a specific year and month in 'YYYY-MM' format."
        )
    ]

    agent = create_tool_calling_agent(llm, tools, final_prompt)

    agent_executor = AgentExecutor(agent=agent, tools=tools)

    response = agent_executor.invoke({"input": question})

    # print(response['output'])

    return response

def generate_hw03(question2, question3):
    pass
    
def generate_hw04(question):
    pass
    
def demo(question):
    llm = AzureChatOpenAI(
            model=gpt_config['model_name'],
            deployment_name=gpt_config['deployment_name'],
            openai_api_key=gpt_config['api_key'],
            openai_api_version=gpt_config['api_version'],
            azure_endpoint=gpt_config['api_base'],
            temperature=gpt_config['temperature']
    )
    message = HumanMessage(
            content=[
                {"type": "text", "text": question},
            ]
    )
    response = llm.invoke([message])
    
    return response

# if __name__ == "__main__":
#     question = "2024年台灣10月紀念日有哪些?"
    # generate_hw01(question)
    # generate_hw02(question)