import os, textwrap, json, yaml, sys

base_path = 'agent_forge_project'

file_contents = {
    # Root level files
    'README.md': textwrap.dedent('''
        # Agent Forge
        
        Agent Forge is a modular, extensible workbench for designing, building, testing and evolving AI agents.
        
        This repository provides a complete baseline implementation covering:
        
        * Declarative component definitions (agents, skills, tools, ethics, teams).
        * A Behaviour Tree (BT) strategy engine.
        * Basic Retrieval-Augmented Generation (RAG) support.
        * An evaluation harness with structured logging and trace analysis.
        * A Streamlit UI for manual experimentation.
        
        ## Quick start
        
        ```bash
        python -m venv .venv && source .venv/bin/activate  # or activate on Windows
        pip install -r requirements.txt
        python run_forge.py --agent simple_agent_v5 --prompt "2 + 2?"
        ```
        
        See the `docs/` folder and inline code comments for full details.
    '''),

    'requirements.txt': textwrap.dedent('''
        PyYAML>=6.0
        pydantic>=2.5
        requests>=2.31
        streamlit>=1.30
        langchain>=0.1
        langchain-community>=0.0.20
        langchain-ollama>=0.1
        duckduckgo-search>=5.0
        pypdf>=4.0
        langchain-text-splitters>=0.0.1
        chromadb>=0.4
    '''),

    'config.yaml': textwrap.dedent('''
        # Global Forge Settings
        ollama_api_url: "http://localhost:11434/api/generate"
        ollama_embedding_url: "http://localhost:11434"
        
        default_generation_model: "qwen2"
        default_embedding_model: "nomic-embed-text"
        default_llm_judge_model: "qwen2"
        
        vector_store_path: "./chroma_db"
        vector_store_collection: "agent_forge_docs"
        
        log_level: INFO
        agent_log_file: "logs/agent_execution.jsonl"
        evaluation_log_file: "logs/evaluation_results.jsonl"
        
        definitions_base_path: "definitions"
        strategies_base_path: "strategies"
        test_cases_base_path: "test_cases"
    '''),

    '.gitignore': textwrap.dedent('''
        __pycache__/
        .venv/
        *.pyc
        logs/
        chroma_db/
    '''),

    # ---------------- forge_core ----------------
    'forge_core/__init__.py': '"""Core logic package for Agent Forge.""\n',

    'forge_core/schemas.py': textwrap.dedent('''
        """Pydantic data-models for every declarative component type."""
        from pydantic import BaseModel, Field
        from typing import List, Dict, Any, Optional, Literal
        
        class ComponentDefinition(BaseModel):
            id: str = Field(..., description="Unique identifier")
            description: str
            implementation: str = Field(..., description="python dotted path to the implementation class")
        
        class InputOutputSchema(BaseModel):
            input_schema: Optional[Dict[str, Any]] = None
            output_schema: Optional[Dict[str, Any]] = None
        
        class ToolDefinition(ComponentDefinition, InputOutputSchema):
            pass
        
        class SkillDefinition(ComponentDefinition, InputOutputSchema):
            required_tools: List[str] = Field(default_factory=list)
        
        class AgentDefinition(ComponentDefinition):
            system_prompt: str
            model_config: Dict[str, Any] = Field(default_factory=dict)
            allowed_skills: List[str] = Field(default_factory=list)
            allowed_tools: List[str] = Field(default_factory=list)
            strategy_definition_id: Optional[str] = None
            worker_agents: Optional[Dict[str, str]] = None
            ethical_framework_ids: List[str] = Field(default_factory=list)
        
        class EthicalPrinciple(BaseModel):
            id: str
            statement: str
            keywords_check: Optional[Dict[str, List[str]]] = None
        
        class EthicalFrameworkDefinition(ComponentDefinition):
            principles: List[EthicalPrinciple]
        
        class TeamDefinition(ComponentDefinition):
            coordinator_agent_id: str
            worker_agents: Dict[str, str]
            coordination_protocol: Literal['Hierarchical'] = 'Hierarchical'
            shared_state_schema: Optional[Dict[str, Any]] = None
        
        class Checkpoint(BaseModel):
            criteria: str
            points: int = Field(default=1, ge=0)
        
        class TestCaseDefinition(BaseModel):
            test_case_id: str
            description: Optional[str] = None
            agent_or_team_id_to_test: str
            input_prompt: str
            expected_output_keywords: Optional[List[str]] = None
            checkpoints: List[Checkpoint] = Field(default_factory=list)
            ethical_checkpoints: List[Checkpoint] = Field(default_factory=list)
            metadata: Dict[str, Any] = Field(default_factory=dict)
    '''),

    'forge_core/forge_logging.py': textwrap.dedent('''
        """Structured JSON logging helpers."""
        import logging, json, os, sys, uuid
        from datetime import datetime
        from typing import Dict, Any, Optional
        
        LOG_DIR = os.path.join(os.getcwd(), 'logs')
        os.makedirs(LOG_DIR, exist_ok=True)
        AGENT_LOG_FILE = os.path.join(LOG_DIR, 'agent_execution.jsonl')
        EVAL_LOG_FILE  = os.path.join(LOG_DIR, 'evaluation_results.jsonl')
        
        class _JsonFormatter(logging.Formatter):
            def format(self, record):
                base = {
                    'timestamp': datetime.utcnow().isoformat(),
                    'level': record.levelname,
                    'logger': record.name,
                }
                if isinstance(record.msg, (dict, list)):
                    base['data'] = record.msg
                else:
                    base['message'] = record.getMessage()
                if record.exc_info:
                    base['exception'] = self.formatException(record.exc_info)
                # include all extras
                base.update(getattr(record, 'extra_data', {}))
                return json.dumps(base, default=str)
        
        def _setup(json_path):
            handler = logging.FileHandler(json_path)
            handler.setFormatter(_JsonFormatter())
            logger = logging.getLogger(json_path)
            logger.setLevel(logging.INFO)
            logger.addHandler(handler)
            logger.propagate = False
            return logger
        
        agent_logger = _setup(AGENT_LOG_FILE)
        harness_logger = _setup(EVAL_LOG_FILE)
        
        def log_agent_step(run_id:str, component_type:str, component_name:str, event_type:str, data:Dict[str,Any], step_id:str, parent_step_id:Optional[str]=None):
            agent_logger.info(data, extra={'extra_data':{
                'run_id':run_id,
                'step_id':step_id,
                'parent_step_id':parent_step_id,
                'component_type':component_type,
                'component_name':component_name,
                'event_type':event_type
            }})
        
        def log_harness_event(data:Dict[str,Any]):
            harness_logger.info(data)
    '''),

    'forge_core/component_registry.py': textwrap.dedent('''
        """Load YAML component definitions into memory and validate."""
        import os, yaml
        from typing import Dict, Type, Optional, Union, List
        from pydantic import ValidationError
        from .schemas import AgentDefinition, SkillDefinition, ToolDefinition, EthicalFrameworkDefinition, TeamDefinition, TestCaseDefinition
        from .forge_logging import harness_logger as logger
        
        Definition = Union[AgentDefinition, SkillDefinition, ToolDefinition, EthicalFrameworkDefinition, TeamDefinition, TestCaseDefinition]
        _MAP: Dict[str, Type[Definition]] = {
            'agents':AgentDefinition,
            'skills':SkillDefinition,
            'tools':ToolDefinition,
            'ethics':EthicalFrameworkDefinition,
            'teams':TeamDefinition,
            'test_cases':TestCaseDefinition
        }
        
        class ComponentRegistry:
            def __init__(self, base_path:str='definitions'):
                self.base_path = base_path
                self.definitions: Dict[str, Dict[str, Definition]] = {k:{} for k in _MAP}
                self._load()
            
            def _load(self):
                for sub, model in _MAP.items():
                    p = os.path.join(self.base_path, sub)
                    if not os.path.isdir(p):
                        continue
                    for fn in os.listdir(p):
                        if not fn.endswith(('.yaml','.yml')):
                            continue
                        fp = os.path.join(p, fn)
                        with open(fp,'r',encoding='utf-8') as f:
                            try:
                                data = yaml.safe_load(f)
                                obj = model(**data)
                                self.definitions[sub][obj.id] = obj
                            except (ValidationError, yaml.YAMLError) as e:
                                logger.error({ 'event':'definition_load_failed', 'file':fp, 'error':str(e) })
                logger.info({ 'event':'registry_loaded', 'stats':{k:len(v) for k,v in self.definitions.items()} })
            
            def get(self, component_type:str, component_id:str):
                return self.definitions.get(component_type, {}).get(component_id)
            
            def reload(self):
                self.definitions = {k:{} for k in _MAP}
                self._load()
    '''),

    'forge_core/agent_builder.py': textwrap.dedent('''
        """Instantiate agents from their YAML definitions."""
        import importlib, inspect
        from typing import List, Any, Dict, Optional, Type
        from .component_registry import ComponentRegistry
        from .forge_logging import harness_logger as logger
        from capabilities.base_capability import BaseSkill, BaseTool
        from agents.base_agent import BaseAgent
        
        class AgentBuilder:
            def __init__(self, registry:ComponentRegistry):
                self.registry = registry
            
            def _import(self, dotted:str):
                mod, cls = dotted.rsplit('.',1)
                m = importlib.import_module(mod)
                return getattr(m, cls)
            
            def _build_caps(self, ids:List[str], ctype:str):
                output = []
                for cid in ids:
                    defn = self.registry.get(f'{ctype}s', cid)
                    if not defn:
                        logger.error({'event':'missing_definition', 'type':ctype, 'id':cid})
                        continue
                    cls = self._import(defn.implementation)
                    base = BaseSkill if ctype=='skill' else BaseTool
                    if not issubclass(cls, base):
                        raise TypeError(f"{cls} must inherit {base}")
                    output.append(cls(definition=defn.model_dump()))
                return output
            
            def build_agent(self, agent_id:str):
                defn = self.registry.get('agents', agent_id)
                if not defn:
                    logger.error({'event':'agent_not_found','id':agent_id})
                    return None
                skills = self._build_caps(defn.allowed_skills, 'skill')
                tools  = self._build_caps(defn.allowed_tools,  'tool')
                cls = self._import(defn.implementation)
                if not issubclass(cls, BaseAgent):
                    raise TypeError('Implementation must inherit BaseAgent')
                init_sig = inspect.signature(cls.__init__)
                kwargs:Dict[str,Any] = { 'agent_config': defn.model_dump() }
                if 'skills' in init_sig.parameters: kwargs['skills']=skills
                if 'tools'  in init_sig.parameters: kwargs['tools']=tools
                return cls(**kwargs)
    '''),

    'forge_core/behavior_tree.py': textwrap.dedent('''
        """Very small Behaviour Tree engine with YAML loader."""
        import yaml, uuid
        from typing import Dict, Any, List
        
        class Status:
            SUCCESS='SUCCESS'
            FAILURE='FAILURE'
            RUNNING='RUNNING'
        
        class Node:
            def __init__(self, name:str, children:List['Node']=None, action=None):
                self.name=name
                self.children=children or []
                self.action=action  # callable
            def tick(self, context:Dict[str,Any]):
                if self.action:
                    return self.action(context)
                raise NotImplementedError
        
        class Sequence(Node):
            def tick(self, context):
                for c in self.children:
                    res=c.tick(context)
                    if res!=Status.SUCCESS:
                        return res
                return Status.SUCCESS
        
        class Selector(Node):
            def tick(self, context):
                for c in self.children:
                    res=c.tick(context)
                    if res==Status.SUCCESS:
                        return Status.SUCCESS
                return Status.FAILURE
        
        class Action(Node):
            pass
        
        _K2C = {
            'Sequence':Sequence,
            'Selector':Selector,
            'Action':Action
        }
        
        def _parse_node(d):
            ntype=list(d.keys())[0]
            spec=d[ntype]
            if ntype in ('Sequence','Selector'):
                children=[_parse_node(c) for c in spec['children']]
                return _K2C[ntype](spec.get('name',ntype),children)
            if ntype=='Action':
                return Action(spec['name'], action=lambda ctx, s=spec: ctx['agent'].run_action(s['name'], ctx))
            raise ValueError(f'Unknown node type {ntype}')
        
        def load_bt(yaml_path:str):
            with open(yaml_path,'r',encoding='utf-8') as f:
                data=yaml.safe_load(f)
            return _parse_node(data['root'])
    '''),

    'forge_core/evaluation.py': textwrap.dedent('''
        """Simple evaluation harness that runs agents against test cases."""
        import uuid, yaml
        from typing import Dict, Any, List
        from .forge_logging import log_harness_event
        from .component_registry import ComponentRegistry
        from .agent_builder import AgentBuilder
        
        class EvaluationHarness:
            def __init__(self, registry:ComponentRegistry):
                self.registry=registry
                self.builder=AgentBuilder(registry)
            
            def _run_test(self, tc) -> Dict[str,Any]:
                run_id=str(uuid.uuid4())
                agent=self.builder.build_agent(tc.agent_or_team_id_to_test)
                if not agent:
                    return {'run_id':run_id, 'error':'agent_build_failed'}
                output=agent.run(tc.input_prompt)
                passed=True
                if tc.expected_output_keywords:
                    passed=all(k.lower() in str(output).lower() for k in tc.expected_output_keywords)
                result={'run_id':run_id,'agent':tc.agent_or_team_id_to_test,'input':tc.input_prompt,'output':output,'passed':passed}
                log_harness_event(result)
                return result
            
            def run_all(self):
                cases:List= list(self.registry.definitions.get('test_cases', {}).values())
                return [self._run_test(tc) for tc in cases]
    '''),

    'forge_core/trace_loader.py': textwrap.dedent('''
        import json
        from typing import List, Dict, Any
        
        def load_trace(path:str)->List[Dict[str,Any]]:
            with open(path,'r',encoding='utf-8') as f:
                return [json.loads(line) for line in f if line.strip()]
    '''),

    'forge_core/llm_judge.py': textwrap.dedent('''
        """Minimal wrapper for calling a local Ollama model to judge responses."""
        import requests, json
        
        def judge(prompt:str, response:str, model:str='qwen2'):
            payload={
                'model':model,
                'prompt':f'You are an impartial judge.\nPrompt:{prompt}\nAnswer:{response}\nGive a score 0-10 and a short justification.'
            }
            r=requests.post('http://localhost:11434/api/generate',json=payload,timeout=60)
            r.raise_for_status()
            return r.json()['response']
    '''),

    'forge_core/safety_guardrails.py': textwrap.dedent('''
        """Very simple keyword based guardrails."""
        FORBIDDEN=['bomb','terror','attack']
        def check_text(txt:str):
            for bad in FORBIDDEN:
                if bad in txt.lower():
                    return False, f'Contains forbidden word: {bad}'
            return True, 'ok'
    '''),

    # ------------- capabilities ---------------
    'capabilities/__init__.py': '',

    'capabilities/base_capability.py': textwrap.dedent('''
        from abc import ABC, abstractmethod
        from typing import Dict, Any
        
        class BaseCapability(ABC):
            def __init__(self, definition:Dict[str,Any]):
                self.id=definition.get('id','UnknownCapability')
                self.description=definition.get('description','')
                self.definition=definition
            @abstractmethod
            def execute(self,*args,**kwargs)->Dict[str,Any]:
                ...
        
        class BaseSkill(BaseCapability):
            pass
        
        class BaseTool(BaseCapability):
            pass
    '''),

    'capabilities/math_skill.py': textwrap.dedent('''
        import operator, uuid
        from typing import Dict, Any
        from capabilities.base_capability import BaseSkill
        from forge_core.forge_logging import log_agent_step
        
        class MathSkill(BaseSkill):
            OPS={ 'add':operator.add, 'subtract':operator.sub, 'multiply':operator.mul, 'divide':operator.truediv }
            def execute(self, run_id:str, parent_step_id:str=None, **kwargs)->Dict[str,Any]:
                step_id=str(uuid.uuid4())
                log_agent_step(run_id,'Skill',self.id,'start',kwargs,step_id,parent_step_id)
                op=kwargs.get('operation')
                a,b=kwargs.get('num1'), kwargs.get('num2')
                if op not in self.OPS:
                    res={'error':'unsupported operation'}
                else:
                    try:
                        res={'result': self.OPS[op](a,b)}
                    except Exception as e:
                        res={'error':str(e)}
                log_agent_step(run_id,'Skill',self.id,'end',res,str(uuid.uuid4()),step_id)
                return res
    '''),

    'capabilities/web_search_tool.py': textwrap.dedent('''
        import uuid
        from typing import Dict, Any
        from duckduckgo_search import DDGS
        from capabilities.base_capability import BaseTool
        from forge_core.forge_logging import log_agent_step
        
        class WebSearchTool(BaseTool):
            def execute(self, run_id:str, parent_step_id:str=None, **kwargs)->Dict[str,Any]:
                step_id=str(uuid.uuid4())
                log_agent_step(run_id,'Tool',self.id,'start',kwargs,step_id,parent_step_id)
                query=kwargs.get('query')
                n=kwargs.get('max_results',3)
                if not query:
                    res={'error':'query required'}
                else:
                    with DDGS() as ddgs:
                        hits=list(ddgs.text(query,max_results=n))
                    res={'results':hits}
                log_agent_step(run_id,'Tool',self.id,'end',res,str(uuid.uuid4()),step_id)
                return res
    '''),

    # ------------- agents ---------------
    'agents/__init__.py': '',

    'agents/base_agent.py': textwrap.dedent('''
        from abc import ABC, abstractmethod
        from typing import Any, Dict
        
        class BaseAgent(ABC):
            def __init__(self, agent_config:Dict[str,Any]):
                self.id = agent_config['id']
                self.config=agent_config
            @abstractmethod
            def run(self, prompt:str):
                ...
            def run_action(self, action_name:str, ctx:Dict[str,Any]):
                raise NotImplementedError('Action routing not implemented')
    '''),

    'agents/simple_agent.py': textwrap.dedent('''
        import uuid
        from typing import List, Any, Dict
        from agents.base_agent import BaseAgent
        from capabilities.base_capability import BaseSkill, BaseTool
        from forge_core.forge_logging import log_agent_step
        
        class SimpleAgent(BaseAgent):
            def __init__(self, agent_config:Dict[str,Any], skills:List[BaseSkill]=None, tools:List[BaseTool]=None):
                super().__init__(agent_config)
                self.skills={s.id:s for s in (skills or [])}
                self.tools ={t.id:t for t in (tools or [])}
            
            def run_action(self, action_name:str, ctx:Dict[str,Any]):
                if action_name=='math.add':
                    skill=self.skills.get('MathSkill_v1')
                    return skill.execute(ctx['run_id'], ctx.get('step_id'), operation='add', num1=ctx['a'], num2=ctx['b'])
                raise ValueError(f'Unknown action {action_name}')
            
            def run(self, prompt:str):
                run_id=str(uuid.uuid4())
                step_id=str(uuid.uuid4())
                log_agent_step(run_id,'Agent',self.id,'start',{'prompt':prompt},step_id)
                # naive echo agent
                output=f"ECHO: {prompt}"
                log_agent_step(run_id,'Agent',self.id,'end',{'output':output},str(uuid.uuid4()),step_id)
                return output
    '''),

    'agents/coordinator_agent.py': textwrap.dedent('''
        from typing import Dict, Any
        from agents.base_agent import BaseAgent
        # For brevity coordinator just proxies to a single worker
        class CoordinatorAgent(BaseAgent):
            def __init__(self, agent_config:Dict[str,Any], builder=None, registry=None, **kwargs):
                super().__init__(agent_config)
                self.builder=builder
                self.registry=registry
                self.workers={ role:self.builder.build_agent(aid) for role,aid in (agent_config.get('worker_agents') or {}).items() }
            def run(self, prompt:str):
                worker=list(self.workers.values())[0]
                return worker.run(prompt)
    '''),

    'agents/bt_agent.py': textwrap.dedent('''
        from typing import Dict, Any
        import uuid, os
        from agents.base_agent import BaseAgent
        from forge_core.behavior_tree import load_bt, Status
        from forge_core.forge_logging import log_agent_step
        
        class BTAAgent(BaseAgent):
            def __init__(self, agent_config:Dict[str,Any], skills=None, tools=None):
                super().__init__(agent_config)
                self.run_id=str(uuid.uuid4())
                strat_id=agent_config['strategy_definition_id']
                path=os.path.join('strategies',f'{strat_id}.yaml')
                self.bt=load_bt(path)
                self.context={'agent':self,'run_id':self.run_id}
            
            def run_action(self, action_name:str, ctx:Dict[str,Any]):
                # stub: just echo
                return {'action':action_name, 'status':'ok'}
            
            def run(self, prompt:str):
                self.context['prompt']=prompt
                res=self.bt.tick(self.context)
                return res
    '''),

    # ------------- higher level scripts ---------------
    'config_loader.py': textwrap.dedent('''
        import yaml, os, sys
        def load_config(path:str='config.yaml'):
            if not os.path.isfile(path):
                print('Config file missing', file=sys.stderr)
                return {}
            with open(path,'r') as f:
                return yaml.safe_load(f) or {}
    '''),

    'run_forge.py': textwrap.dedent('''
        import argparse
        from forge_core.component_registry import ComponentRegistry
        from forge_core.agent_builder import AgentBuilder
        
        def main():
            ap=argparse.ArgumentParser()
            ap.add_argument('--agent',required=True)
            ap.add_argument('--prompt',required=True)
            args=ap.parse_args()
            reg=ComponentRegistry()
            builder=AgentBuilder(reg)
            agent=builder.build_agent(args.agent)
            if not agent:
                print('Could not build agent')
                return
            print(agent.run(args.prompt))
        
        if __name__=='__main__':
            main()
    '''),

    'forge_ui.py': textwrap.dedent('''
        import streamlit as st
        from forge_core.component_registry import ComponentRegistry
        from forge_core.agent_builder import AgentBuilder
        
        st.title('Agent Forge Workbench')
        prompt=st.text_input('Prompt')
        if 'builder' not in st.session_state:
            st.session_state.registry=ComponentRegistry()
            st.session_state.builder=AgentBuilder(st.session_state.registry)
        agent_id=st.selectbox('Agent', st.session_state.registry.list_ids('agents'))
        if st.button('Run'):
            agent=st.session_state.builder.build_agent(agent_id)
            with st.spinner('Running…'):
                out=agent.run(prompt)
            st.markdown(f'**Output**\n\n{out}')
    '''),

    # ---------- definitions examples ---------
    'definitions/agents/simple_agent_v5.yaml': textwrap.dedent('''
        id: simple_agent_v5
        description: Simple echo agent
        implementation: agents.simple_agent.SimpleAgent
        system_prompt: "You are a helpful AI assistant."
        model_config: {model: qwen2, temperature: 0.3}
        allowed_skills: [math_skill_v1]
        allowed_tools: []
    '''),

    'definitions/skills/math_skill_v1.yaml': textwrap.dedent('''
        id: math_skill_v1
        description: Basic arithmetic operations
        implementation: capabilities.math_skill.MathSkill
        input_schema:
          properties:
            operation: {type: string}
            num1: {type: number}
            num2: {type: number}
        output_schema: {type: object}
    '''),

    'definitions/tools/web_search_tool_v1.yaml': textwrap.dedent('''
        id: web_search_tool_v1
        description: Search the web via DuckDuckGo
        implementation: capabilities.web_search_tool.WebSearchTool
        input_schema:
          properties:
            query: {type: string}
            max_results: {type: integer}
    '''),

    'strategies/rag_search_strategy.yaml': textwrap.dedent('''
        root:
          Sequence:
            name: root
            children:
              - Action:
                  name: retrieve
              - Action:
                  name: generate_answer
    '''),

    'test_cases/basic_math.yaml': textwrap.dedent('''
        test_case_id: tc_basic_math
        description: simple math
        agent_or_team_id_to_test: simple_agent_v5
        input_prompt: "What is 2 + 2?"
        expected_output_keywords: ['4']
    '''),
}

# Create all paths and write files
for rel_path, content in file_contents.items():
    abs_path = os.path.join(base_path, rel_path)
    os.makedirs(os.path.dirname(abs_path), exist_ok=True)
    with open(abs_path, 'w', encoding='utf-8') as f:
        f.write(content.lstrip('\n'))

print(f'Project skeleton written to ./{base_path}')