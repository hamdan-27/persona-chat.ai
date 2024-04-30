from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate, MessagesPlaceholder, PromptTemplate
from langchain_experimental.agents.agent_toolkits.pandas.base import create_pandas_dataframe_agent
from langchain_community.document_loaders import TextLoader, PyMuPDFLoader
from langchain_experimental.agents.agent_toolkits import create_csv_agent
from langchain_experimental.tools.python.tool import PythonAstREPLTool
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.tools.retriever import create_retriever_tool
from langchain_text_splitters import CharacterTextSplitter
from langchain.agents.mrkl.base import ZeroShotAgent
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain.chains.llm import LLMChain
from langchain_openai import ChatOpenAI
from config import app, db
import pandas as pd
import models

PREFIX = """
{user_prompt}. You are working with a pandas dataframe in Python. The name of the dataframe is `df`. You can answer general messages liek greetings.
You should use the tools below to answer the question posed of you:"""

FORMAT_INSTRUCTIONS = """Use the following format:

Input: the input question you must answer
Thought: Do I need to use a tool? (Yes or No)
Action: the action to take, should be one of [{tool_names}] if using a tool, otherwise answer on your own.
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question"""

def create_rag_agent(user_prompt, datatype, filepath, llm=ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=0.1)):
    if datatype == "pdf":
        loader = PyMuPDFLoader(app.config["UPLOAD_FOLDER"] + filepath)
    elif datatype == "txt":
        loader = TextLoader(app.config["UPLOAD_FOLDER"] + filepath)
    
    documents = loader.load()

    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    texts = text_splitter.split_documents(documents)
    embeddings = OpenAIEmbeddings()
    database = FAISS.from_documents(texts, embeddings)

    retriever = database.as_retriever()

    tool = create_retriever_tool(
        retriever,
        "search_document",
        "Searches and returns information from the document.",
    )
    tools = [tool]

    prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate(
            prompt=PromptTemplate(input_variables=[], template=f'You are a helpful assistant. {user_prompt}')),
        MessagesPlaceholder(variable_name='chat_history', optional=True),
        HumanMessagePromptTemplate(prompt=PromptTemplate(
            input_variables=['input'], template='{input}')),
        MessagesPlaceholder(variable_name='agent_scratchpad')
    ])

    agent = create_openai_tools_agent(llm, tools, prompt)
    return AgentExecutor(agent=agent, tools=tools)


def create_pandas_agent(user_prompt, datatype, filepath, 
                        llm=ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=0.1)):
    if datatype == "csv":
        df = pd.read_csv(app.config["UPLOAD_FOLDER"] + filepath)
    elif datatype == "xlsx":
        df = pd.read_excel(app.config["UPLOAD_FOLDER"] + filepath)

    input_variables = ["input", "agent_scratchpad"]
    tools = [PythonAstREPLTool(locals={"df": df})]
    prompt = ZeroShotAgent.create_prompt(
        tools,
        prefix=PREFIX.format(user_prompt=user_prompt),
        format_instructions=FORMAT_INSTRUCTIONS,
        input_variables=input_variables,
    )
    partial = prompt.partial()

    llm_chain = LLMChain(
        llm=llm,
        prompt=partial,
    )

    tool_names = [tool.name for tool in tools]
    agent = ZeroShotAgent(
        llm_chain=llm_chain,
        allowed_tools=tool_names,
    )

    return AgentExecutor.from_agent_and_tools(
        agent=agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors=True,
    )

    # return create_pandas_dataframe_agent(
    #     llm=llm,
    #     df=df,
    #     prefix=user_prompt,
    #     verbose=True,
    #     handle_parsing_errors=True,
    # )

