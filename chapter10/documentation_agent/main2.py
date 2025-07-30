import operator  # 標準演算子ライブラリ
from typing import Annotated, Any, Optional  # 型ヒント用標準ライブラリ

from dotenv import load_dotenv  # .envから環境変数を読み込むライブラリ
from langchain_core.output_parsers import StrOutputParser  # LangChainの出力パーサ
from langchain_core.prompts import (
    ChatPromptTemplate,
)  # LangChainのプロンプトテンプレート
from langchain_openai import ChatOpenAI  # OpenAIのLLMラッパー
from langgraph.graph import END, StateGraph  # LangGraphのグラフ構築用
from pydantic import BaseModel, Field  # データバリデーション用モデル

# .envファイルから環境変数を読み込む
load_dotenv()


# ペルソナを表すデータモデル
class Persona(BaseModel):
    name: str = Field(..., description="ペルソナの名前")
    background: str = Field(..., description="ペルソナの持つ背景")


# ペルソナのリストを表すデータモデル
class Personas(BaseModel):
    # ペルソナのリスト
    personas: list[Persona] = Field(
        default_factory=list,
        description="ペルソナのリスト",
    )


# インタビュー内容を表すデータモデル
class Interview(BaseModel):
    persona: Persona = Field(..., description="インタビュー対象のペルソナ")
    question: str = Field(..., description="インタビューでの質問")
    answer: str = Field(..., description="インタビューでの回答")


# インタビュー結果のリストを表すデータモデル
class InterviewResult(BaseModel):
    interviews: list[Interview] = Field(
        default_factory=list,
        description="インタビューの結果リスト",
    )


# 評価の結果を表すデータモデル
class EvaluationResult(BaseModel):
    reason: str = Field(..., description="判断の理由")
    is_sufficient: bool = Field(..., description="情報が十分かどうか")


# 要件定義生成AIエージェントのステート
class InterviewState(BaseModel):
    user_request: str = Field(..., description="ユーザーからのリクエスト")
    personas: list[Persona] = Field(
        default_factory=list,
        description="生成されたペルソナのリスト",
    )
    interviews: list[Interview] = Field(
        default_factory=list,
        description="実施されたインタビューのリスト",
    )
    requirement_doc: str = Field(default="", description="生成された要件定義")
    iteration: int = Field(
        default=0,
        description="ペルソナ生成とインタビューの反復回数",
    )
    is_information_sufficient: bool = Field(
        default=False,
        description="情報が十分かどうか",
    )


# ペルソナを生成するクラス
class PersonaGenerator:
    # 初期化メソッド。LLMと生成人数を設定
    def __init__(self, llm: ChatOpenAI, k: int = 5):
        # LLMに構造化出力を指定
        self.llm = llm.with_structured_output(Personas)
        # 生成するペルソナ数
        self.k = k

    # ペルソナ生成を実行するメソッド
    def run(self, user_request: str) -> Personas:
        # プロンプトテンプレートを定義
        prompt = ChatPromptTemplate.from_messages(
            [
                # システムメッセージ  # "system"
                (
                    "system",
                    "あなたはユーザーインタビュー用のペルソナを作成する専門家です。",
                ),
                # ユーザーメッセージ  # "human"
                (
                    "human",
                    f" 以下のユーザーリクエストに関するインタビュー用に{self.k}人の多様なペルソナを生成してください。\n\n"
                    "ユーザーリクエスト：{user_request}\n\n"
                    "各ペルソナには名前と簡単な背景を含めてください。年齢、性別、職業、技術的専門知識において多様性を確保してください",
                ),
            ]
        )
        # プロンプトとLLMをチェーン
        chain = prompt | self.llm
        # ペルソナ生成を実行
        return chain.invoke({"user_request": user_request})


# インタビュー実施のためのロジックをまとめたクラス
class InterviewConductor:
    # LLMを初期化するコンストラクタ
    def __init__(self, llm: ChatOpenAI):
        # LLMインスタンスを保持
        self.llm = llm

    # インタビューの一連の流れ（質問生成→回答生成→インタビュー作成）を実行するメソッド
    def run(self, user_request: str, personas: list[Persona]) -> InterviewResult:
        # 質問を生成
        questions = self._generate_questions(
            user_request=user_request, personas=personas
        )
        # 回答を生成
        answers = self._generate_answers(personas=personas, questions=questions)
        # インタビューオブジェクトを作成
        interviews = self._create_interviews(
            personas=personas, questions=questions, answers=answers
        )
        # インタビュー結果を返す
        return InterviewResult(interviews=interviews)

    # ペルソナごとに質問を生成するメソッド
    def _generate_questions(
        self, user_request: str, personas: list[Persona]
    ) -> list[str]:
        # 質問生成用のプロンプトテンプレートを作成
        question_prompt = ChatPromptTemplate.from_messages(
            [
                # システムメッセージを設定
                (
                    "system",
                    "あなたはユーザー要件に基づいて適切な質問を生成する専門家です",
                ),
                # ユーザーメッセージを設定
                (
                    "human",
                    "以下のペルソナに関するユーザーリクエストについて1つの質問を生成してください。\n\n"
                    "ユーザーリクエスト：{user_request}\n"
                    "ペルソナ：{persona_name} - {persona_background}\n\n"
                    "質問は具体的で、このペルソナの視点から重要な情報を引き出すように設計してください。",
                ),
            ]
        )
        # プロンプト・LLM・出力パーサーをチェーン
        question_chain = question_prompt | self.llm | StrOutputParser()
        # ペルソナごとに質問生成用のクエリを作成
        question_queries = [
            {
                "user_request": user_request,
                "persona_name": persona.name,
                "persona_background": persona.background,
            }
            for persona in personas
        ]
        # バッチで質問を生成して返す
        return question_chain.batch(question_queries)

    # 回答生成メソッドの定義
    def _generate_answers(
        self, personas: list[Persona], questions: list[str]
    ) -> list[str]:
        # 回答生成用のプロンプトテンプレートを作成
        answer_prompt = ChatPromptTemplate.from_messages(
            [
                # システムメッセージ：ペルソナとして回答する旨を指示
                (
                    "system",
                    "あなたは以下のペルソナとして回答しています：{persona_name} - {persona_background}",
                ),
                # ヒューマンメッセージ：質問内容を指定
                ("human", "質問：{question}"),
            ]
        )
        # プロンプト・LLM・出力パーサーをチェーン
        answer_chain = answer_prompt | self.llm | StrOutputParser()

        # ペルソナごとに回答生成用のクエリを作成
        answer_questions = [
            {
                "persona_name": persona.name,
                "persona_background": persona.background,
                "question": question,
            }
            for persona, question in zip(personas, questions)
        ]

        # バッチで回答を生成して返す
        return answer_chain.batch(answer_questions)

    # Interviewオブジェクトのリストを生成して返す
    def _create_interviews(
        self, personas: list[Persona], questions: list[str], answers: list[str]
    ) -> list[Interview]:
        # 各ペルソナ・質問・回答の組み合わせでInterviewを生成
        return [
            Interview(persona=persona, question=question, answer=answer)
            for persona, question, answer in zip(
                personas, questions, answers
            )  # 3つのリストを同時にループ
        ]


# インタビュー結果とユーザーリクエストから要件情報の十分性を評価するクラス
class InformationEvaluator:
    # LLMを初期化し、構造化出力を設定
    def __init__(self, llm: ChatOpenAI):
        # LLMにEvaluationResult型の構造化出力を設定
        self.llm = llm.with_structured_output(EvaluationResult)

    # ユーザーリクエストとインタビュー結果から情報の十分性を評価するメソッド
    def run(self, user_request: str, interviews: list[Interview]) -> EvaluationResult:
        # プロンプトテンプレートを作成
        prompt = ChatPromptTemplate.from_messages(
            [
                # システムメッセージ：評価者としての役割を指示
                (
                    "system",
                    "あなたは包括的な要件文章を作成するための情報を十分に評価する専門家です。",
                ),
                # ヒューマンメッセージ：評価対象の情報を指定
                (
                    "human",
                    "以下のユーザーリクエストとインタビュー結果に基づいて、包括的な要件文章を作成するのに十分な情報が集まったかどうかを判断してください。\n\n"
                    "ユーザーリクエスト：{user_request}\n\n"
                    "インタビュー結果：\n{interview_results}",
                ),
            ]
        )
        # プロンプトとLLMをチェーン
        chain = prompt | self.llm
        # チェーンに入力値を渡して評価を実行
        return chain.invoke(
            {
                # ユーザーリクエストを渡す
                "user_request": user_request,
                # インタビュー結果を整形して渡す
                "interview_results": "\n".join(
                    f"ペルソナ：{i.persona.name} - {i.persona.background}\n"
                    f"質問：{i.question}\n回答：{i.answer}\n"
                    for i in interviews  # 各インタビューを整形
                ),
            }
        )


# 要件定義書生成器class RequirementsDocumentGenerator:
class RequirementsDocumentGenerator:
    # LLMインスタンスを受け取り初期化する
    def __init__(self, llm: ChatOpenAI):
        # LLMをインスタンス変数に格納
        self.llm = llm

    # ユーザーリクエストとインタビューリストから要件文章を生成するメソッド
    def run(self, user_request: str, interviews: list[Interview]) -> str:
        # プロンプトテンプレートを作成
        prompt = ChatPromptTemplate.from_messages(
            [
                # システムメッセージ：要件文章作成の専門家として指示
                (
                    "system",
                    "あなたは収集した情報に基づいて要件文章を精査くせ売る専門家です。",
                ),
                # ヒューマンメッセージ：要件文章作成の指示と出力フォーマット指定
                (
                    "human",
                    "以下のユーザーリクエストと複数のペルソナからのインタビュー結果に基づいて、要件文章を作成してください。\n\n"
                    "ユーザーリクエスト：{user_request}\n\n"
                    "インタビュー結果：\n{interview_results}\n"
                    "要件文章には以下のセクションを含めてください：\n"
                    "1. プロジェクト概要\n"
                    "2. 主要機能\n"
                    "3. 非機能要件\n"
                    "4. 制約条件\n"
                    "5. ターゲットユーザー\n"
                    "6. 優先順位\n"
                    "7. リスクと軽減策\n"
                    "出力は必ず日本語でお願いします。\n\n要件文章：",
                ),
            ]
        )
        # プロンプト・LLM・出力パーサーをチェーン
        chain = prompt | self.llm | StrOutputParser()
        # チェーンに入力値を渡して要件文章を生成
        return chain.invoke(
            {
                # ユーザーリクエストを渡す
                "user_request": user_request,
                # インタビュー結果を整形して渡す
                "interview_results": "\n".join(
                    f"ペルソナ：{i.persona.name} - {i.persona.background}\n"
                    f"質問：{i.question}\n回答：{i.answer}\n"
                    for i in interviews
                ),
            }
        )


# 要件定義AIエージェントの全体ワークフローの管理クラス
class DocumentationAgent:
    # エージェントの初期化処理（各種生成器・評価器のセットアップ）
    def __init__(self, llm: ChatOpenAI, k: Optional[int] = None):
        # ペルソナ生成器を初期化
        self.persona_generator = PersonaGenerator(llm=llm, k=k)
        # インタビュー実施器を初期化
        self.interview_conductor = InterviewConductor(llm=llm)
        # 情報十分性評価器を初期化
        self.information_evaluator = InformationEvaluator(llm=llm)
        # 要件定義書生成器を初期化
        self.requirements_generator = RequirementsDocumentGenerator(llm=llm)
        # ワークフローグラフを作成
        self.graph = self._create_graph()

    # ステートグラフ（ワークフロー）の構築
    def _create_graph(self) -> StateGraph:
        # ステートグラフをInterviewStateで初期化
        workflow = StateGraph(InterviewState)
        # ペルソナ生成ノードを追加
        workflow.add_node("generate_personas", self._generate_personas)
        # インタビューノードを追加
        workflow.add_node("conduct_interviews", self._conduct_interviews)
        # 情報評価ノードを追加
        workflow.add_node("evaluate_information", self._evaluate_information)
        # 要件生成ノードを追加
        workflow.add_node("generate_requirements", self._generate_requirements)

        # エントリーポイントを設定
        workflow.set_entry_point("generate_personas")
        # ペルソナ生成→インタビューのエッジを追加
        workflow.add_edge("generate_personas", "conduct_interviews")
        # インタビュー→情報評価のエッジを追加
        workflow.add_edge("conduct_interviews", "evaluate_information")

        # 条件付きエッジ（情報が不十分かつ5回未満なら再度ペルソナ生成、十分なら要件生成へ）
        workflow.add_conditional_edges(
            "evaluate_information",  # 評価ノードから
            lambda state: not state.is_information_sufficient
            and state.iteration < 5,  # 条件
            {True: "generate_personas", False: "generate_requirements"},  # 遷移先
        )
        # 要件生成→終了のエッジを追加
        workflow.add_edge("generate_requirements", END)

        # グラフをコンパイルして返す
        return workflow.compile()

    # ペルソナ生成ノードの処理
    def _generate_personas(self, state: InterviewState) -> dict[str, Any]:
        # ペルソナを生成
        new_personas: Personas = self.persona_generator.run(state.user_request)
        # 新しいペルソナリストとイテレーション回数を返す
        updated_personas = state.personas + new_personas.personas
        update_dict = {"personas": updated_personas, "iteration": state.iteration + 1}
        print(f"DEBUG: _generate_personas returning: {update_dict}")
        return update_dict

    # インタビューノードの処理
    def _conduct_interviews(self, state: InterviewState) -> dict[str, Any]:
        # 直近5人のペルソナに対してインタビューを実施
        new_interviews: InterviewResult = self.interview_conductor.run(
            state.user_request, state.personas[-5:]  # 直近5人
        )
        # インタビュー結果を返す
        updated_interviews = state.interviews + new_interviews.interviews
        update_dict = {"interviews": updated_interviews}
        print(f"DEBUG: _conduct_interviews returning: {update_dict}")
        return update_dict

    # 情報評価ノードの処理
    def _evaluate_information(self, state: InterviewState) -> dict[str, Any]:
        # 情報の十分性を評価
        evaluation_result: EvaluationResult = self.information_evaluator.run(
            state.user_request, state.interviews
        )
        # 評価結果（十分性・理由）を返す
        update_dict = {
            "is_information_sufficient": evaluation_result.is_sufficient,
        }
        print(f"DEBUG: _evaluate_information returning: {update_dict}")  # デバッグ用
        return update_dict

    # 要件定義書生成ノードの処理
    def _generate_requirements(self, state: InterviewState) -> dict[str, Any]:
        # 要件定義書を生成
        requirements_doc: str = self.requirements_generator.run(
            state.user_request, state.interviews
        )
        # 生成した要件定義書を返す
        update_dict = {"requirements_doc": requirements_doc}
        print(f"DEBUG: _generate_requirements returning: {update_dict}")
        return update_dict

    # エージェントの実行（ユーザーリクエストから最終要件定義書まで）
    def run(self, user_request: str) -> str:
        print(
            f"DEBUG: DocumentationAgent.run received user_request: {user_request}"
        )  # デバッグ用
        # 初期状態を作成
        initial_state = InterviewState(user_request=user_request)
        # グラフを実行して最終状態を取得
        final_state = self.graph.invoke(initial_state)
        # 最終的な要件定義書を返す
        return final_state["requirements_doc"]


# コマンドライン引数を受け取り、要件定義書生成エージェントを実行して結果を出力する
def main():
    # コマンドライン引数を解析するargparseをインポート
    import argparse  # コマンドライン引数パーサ

    # 引数パーサのインスタンスを作成
    parser = argparse.ArgumentParser(
        description="ユーザーの要求に基づいて用件定義書を生成します"  # ヘルプ用説明
    )

    # "task"引数を追加（作成したいアプリ内容を指定）
    parser.add_argument(
        "--task",
        type=str,
        help="作成したいアプリケーションについて記載してください",  # ユーザーリクエスト
    )
    # "k"引数を追加（ペルソナ人数の指定）
    parser.add_argument(
        "--k",
        type=int,
        default=5,
        help="生成するペルソナの人数を指定してください(デフォルト:5)",  # ペルソナ人数
    )

    # コマンドライン引数を解析して取得
    args = parser.parse_args()

    # OpenAIのLLMインスタンスを初期化
    llm = ChatOpenAI(model="gpt-4o", temperature=0)  # OpenAI GPT-4oモデル
    # ドキュメントエージェントを初期化
    agent = DocumentationAgent(llm=llm, k=args.k)
    # エージェントを実行し、最終出力（要件定義書）を取得
    final_output = agent.run(user_request=args.task)

    # 生成した要件定義書を出力
    print(final_output)


# スクリプトが直接実行された場合のみmain()を呼び出す
if __name__ == "__main__":
    main()
