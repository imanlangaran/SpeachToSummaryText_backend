from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
import os
import tempfile

from app.services.transcription_service import transcribe_audio
from app.services.summarise_service import summarise_text

from app.db.database import get_db
from app.models import Transcription, User, Prompt, Summary
from app.auth.dependencies import get_current_user

router = APIRouter(prefix="/audio", tags=["audio"])


@router.post("/upload", response_model=None)
async def upload_audio(
    file: UploadFile = File(...),
    prompt: str = "",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # 1. Validate audio file type
    if not file.content_type.startswith("audio/"):
        raise HTTPException(status_code=400, detail="Only audio files are accepted")

    # 2. Save to a temporary location
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name

        transcription = Transcription(
            user_id=current_user.id,
            file_path=tmp_path,
            prompt=prompt,
            status="processing",
        )
        db.add(transcription)
        db.commit()
        db.refresh(transcription)

        # 3. Transcribe using Whisper
        transcript_text = transcribe_audio(tmp_path, prompt=prompt)

        transcription.status = "done"
        transcription.result = transcript_text.strip()
        db.commit()

        # 4. Return transcript
        return {"filename": file.filename, "transcript": transcript_text}

    except Exception as e:
        transcription.status = "failed"
        transcription.error_message = str(e)
        db.commit()
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")

    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

# @router.post('/test_summ', response_model=None)
# def testing(
#     summaryPromptId: int = -1,
#     current_user: User = Depends(get_current_user),
#     db: Session = Depends(get_db),
# ):
#     try:
#         prompt = db.query(Prompt).filter(Prompt.id == summaryPromptId).first()
#         if summaryPromptId == -1 or not prompt:
#             raise HTTPException(status_code=404, detail="Prompt not found")
        
#         transcript_text= '''
#         خلاصه:\n\nدر سال ۱۹۵۴، یک فروشنده به نام ریکیراک وارد رستوران مک‌دونالد شد و متوجه شد که آنجا همه کارها بسیار سیستماتیک و دقیق انجام می‌شود. صاحبان رستوران کارها را به سه بخش «چی»، «چطور» و «چرا» تقسیم کرده و برای حتی ساده‌ترین کارها دستورالعمل مشخص داشتند. این سیستم باعث می‌شد که کارمندان جدید خیلی سریع آموزش ببینند و با همان کیفیت کار کنند. ریکیراک فهمید این مدل قابل تکثیر است و همین زمینه‌ساز گسترش مک‌دونالد شد. پیام اصلی این است که در کسب‌وکار، باید هر کاری که بیش از دو بار تکرار می‌شود با دستورالعمل مدون انجام شود تا سیستم‌پذیر و قابل رشد باشد. در پایان، سؤال می‌شود: کدام کارها فقط شما می‌دانید و اگر شخص جدیدی اضافه شود چقدر سریع می‌تواند جایگزین شود؟
#         '''
        
#         summary = Summary(
#             user_id=current_user.id,
#             status='pending',
#             prompt_id= summaryPromptId
#         )
#         db.add(summary)
#         db.commit()
#         db.refresh(summary)
        
#         summarised_text = summarise_text(transcript_text, prompt)
        
#         summary.status = 'success'
#         summary.summary = summarised_text
#         db.commit()
        
#         return {
#             'sucess' : 'true',
#             'data' : {
#                 'summarise_text' : summarised_text
#             }
#         }
#     except Exception as e:
#         summary.status = 'error'
#         summary.result = str(e)
#         db.commit()
#         raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")

        
    

@router.post("/upload_summarize", response_model=None)
async def upload_audio(
    file: UploadFile = File(...),
    transcribePrompt: str = "",
    summaryPromptId: int = -1,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # 1. Validate audio file type
    if not file.content_type.startswith("audio/"):
        raise HTTPException(status_code=400, detail="Only audio files are accepted")
    
    prompt = db.query(Prompt).filter(Prompt.id == summaryPromptId).first()
    if summaryPromptId == -1 or not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")

    # 2. Save to a temporary location
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name

        transcription = Transcription(
            user_id=current_user.id,
            file_path=tmp_path,
            prompt=transcribePrompt,
            status="processing",
        )
        db.add(transcription)
        db.commit()
        db.refresh(transcription)

        # 3. Transcribe using Whisper
        transcript_text = transcribe_audio(tmp_path, prompt=prompt)

        transcript_text = transcript_text.strip()
        transcription.status = "done"
        transcription.result = transcript_text
        db.commit()

        summary = Summary(
            user_id=current_user.id,
            status='pending',
            prompt_id= summaryPromptId
        )
        db.add(summary)
        db.commit()
        db.refresh(summary)
        
        summarised_text = summarise_text(transcript_text, prompt)
        
        summary.status = 'success'
        summary.summary = summarised_text
        db.commit()
        
        return {
            'sucess' : 'true',
            'data' : {
                'summarise_text' : summarised_text
            }
        }

    except Exception as e:
        transcription.status = "failed"
        transcription.error_message = str(e)
        
        # if summary is not None:
        #     summary.status = 'error'
        #     summary.result = str(e)
        
        db.commit()
        raise HTTPException(status_code=500, detail=f"Transcription/Summarization failed: {str(e)}")

    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
