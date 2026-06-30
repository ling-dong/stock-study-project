"""测验组件 — 单选、多选、判断"""
import streamlit as st
from typing import Optional

from models.quiz import QuizQuestion, QuizResult


def render_quiz(questions: list[dict], chapter_id: str) -> Optional[QuizResult]:
    """渲染一组测验题，返回测验结果或 None（用户尚未提交）"""
    if not questions:
        st.info("本章暂无测验题")
        return None

    parsed = [QuizQuestion.from_dict(q) for q in questions]

    st.markdown("---")
    st.subheader("📝 章节测验")

    # 使用 session_state 存储用户答案
    state_key = f"quiz_answers_{chapter_id}"
    if state_key not in st.session_state:
        st.session_state[state_key] = {}

    answers = st.session_state[state_key]

    # 渲染每一题
    for q in parsed:
        st.markdown(f"**{q.id}.** {q.question}")

        if q.type == "single_choice":
            options = [f"{chr(65+i)}. {opt}" for i, opt in enumerate(q.options)]
            selected = st.radio(
                f"选择答案 {q.id}",
                options=range(len(q.options)),
                format_func=lambda i: options[i],
                key=f"quiz_{chapter_id}_{q.id}",
                index=None,
                label_visibility="collapsed",
            )
            if selected is not None:
                answers[q.id] = selected

        elif q.type == "multi_choice":
            selected = []
            for i, opt in enumerate(q.options):
                if st.checkbox(f"{chr(65+i)}. {opt}", key=f"quiz_{chapter_id}_{q.id}_{i}"):
                    selected.append(i)
            if selected:
                answers[q.id] = selected

        elif q.type == "true_false":
            selected = st.radio(
                f"判断 {q.id}",
                options=[True, False],
                format_func=lambda v: "✅ 正确" if v else "❌ 错误",
                key=f"quiz_{chapter_id}_{q.id}",
                index=None,
                label_visibility="collapsed",
            )
            if selected is not None:
                answers[q.id] = selected

    # 提交按钮
    if st.button("提交答案", key=f"submit_{chapter_id}"):
        if len(answers) < len(parsed):
            st.warning("请完成所有题目后再提交")
            return None

        correct = 0
        for q in parsed:
            user_ans = answers.get(q.id)
            if user_ans == q.answer:
                correct += 1
            elif isinstance(q.answer, list) and isinstance(user_ans, list):
                if set(user_ans) == set(q.answer):
                    correct += 1

        score = correct / len(parsed) if parsed else 0.0

        if score >= 0.8:
            st.success(f"🎉 得分: {correct}/{len(parsed)} ({score:.0%}) — 优秀！")
        elif score >= 0.6:
            st.info(f"📚 得分: {correct}/{len(parsed)} ({score:.0%}) — 通过，继续加油！")
        else:
            st.error(f"📖 得分: {correct}/{len(parsed)} ({score:.0%}) — 建议重新学习本章")

        with st.expander("查看解析"):
            for q in parsed:
                st.markdown(f"**{q.id}**: {q.explanation}")

        del st.session_state[state_key]

        import datetime
        return QuizResult(
            chapter_id=chapter_id,
            total_questions=len(parsed),
            correct_count=correct,
            score=score,
            answers=answers,
            timestamp=datetime.datetime.now().isoformat(),
        )

    return None
