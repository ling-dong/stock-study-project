"""测试进度模型"""
from models.progress import ChapterProgress, LabProgress


def test_chapter_progress_default():
    cp = ChapterProgress(chapter_id="p1_ch1")
    assert cp.completed is False
    assert cp.quiz_score == 0.0
    assert cp.quiz_attempts == 0


def test_chapter_progress_mark_completed():
    cp = ChapterProgress(chapter_id="p1_ch1")
    cp.mark_completed(quiz_score=0.8)
    assert cp.completed is True
    assert cp.quiz_score == 0.8
    assert cp.quiz_attempts == 1
    assert cp.last_accessed is not None


def test_chapter_progress_serialization():
    cp = ChapterProgress(chapter_id="p1_ch1")
    cp.mark_completed(quiz_score=0.75)
    d = cp.to_dict()
    cp2 = ChapterProgress.from_dict(d)
    assert cp2.chapter_id == "p1_ch1"
    assert cp2.completed is True
    assert cp2.quiz_score == 0.75


def test_lab_progress_mark_exercise():
    lp = LabProgress(lab_id="m1")
    lp.mark_exercise_done("ex1")
    assert "ex1" in lp.exercises_done
    lp.mark_exercise_done("ex1")  # 不重复
    assert len(lp.exercises_done) == 1
