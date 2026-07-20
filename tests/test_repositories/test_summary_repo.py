"""Tests for SummaryRepository."""

from app.repositories.summary_repo import SummaryRepository
from app.models.summary import Summary


class TestSummaryRepository:
    def test_create(self, db_session, test_user, test_prompt):
        repo = SummaryRepository(db_session)
        s = repo.create(
            user_id=test_user.id,
            transcription_id=1,
            prompt_id=test_prompt.id,
            status="pending",
        )
        db_session.commit()
        assert s.id is not None
        assert s.status == "pending"

    def test_list_by_transcription(self, db_session, test_user, test_prompt):
        repo = SummaryRepository(db_session)
        # Different prompt_ids to avoid unique constraint violation
        from app.models.prompt import Prompt
        p2 = Prompt(title="P2", content="c2", is_deleted=False)
        db_session.add(p2)
        db_session.commit()
        repo.create(user_id=test_user.id, transcription_id=10, prompt_id=test_prompt.id, status="done")
        repo.create(user_id=test_user.id, transcription_id=10, prompt_id=p2.id, status="pending")
        db_session.commit()
        results = repo.list_by_transcription(10, test_user.id)
        assert len(results) == 2

    def test_list_by_transcription_wrong_user(self, db_session, test_user, test_prompt):
        repo = SummaryRepository(db_session)
        repo.create(user_id=test_user.id, transcription_id=10, prompt_id=test_prompt.id, status="done")
        db_session.commit()
        results = repo.list_by_transcription(10, 99999)
        assert len(results) == 0

    def test_find_existing(self, db_session, test_user, test_prompt):
        repo = SummaryRepository(db_session)
        repo.create(user_id=test_user.id, transcription_id=5, prompt_id=test_prompt.id, status="success")
        db_session.commit()
        found = repo.find_existing(test_user.id, 5, test_prompt.id)
        assert found is not None
        assert found.status == "success"

    def test_find_existing_not_found(self, db_session, test_user, test_prompt):
        repo = SummaryRepository(db_session)
        assert repo.find_existing(test_user.id, 999, test_prompt.id) is None
