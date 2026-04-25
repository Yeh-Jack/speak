"""Course endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.repositories import CourseRepository, CourseVideoRepository, VideoRepository
from app.schemas.course import Course, CourseCreate, CourseUpdate, CourseVideo, ReorderVideosRequest

router = APIRouter()


@router.get("", response_model=list[Course])
async def list_courses(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    """List all courses."""
    repo = CourseRepository(db)
    return await repo.get_all(skip=skip, limit=limit)


@router.get("/{course_id}", response_model=Course)
async def get_course(
    course_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get a course by ID with its videos."""
    repo = CourseRepository(db)
    course = await repo.get_with_videos(course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course


@router.post("", response_model=Course, status_code=status.HTTP_201_CREATED)
async def create_course(
    course_data: CourseCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new course."""
    from app.models.course import Course as CourseModel

    course = CourseModel(
        title=course_data.title,
        description=course_data.description,
        status="pending",
    )

    course_repo = CourseRepository(db)
    course = await course_repo.create(course)

    if course_data.video_ids:
        video_repo = VideoRepository(db)
        course_video_repo = CourseVideoRepository(db)
        from app.models.course import CourseVideo as CourseVideoModel

        for idx, video_id in enumerate(course_data.video_ids):
            video = await video_repo.get_by_id(video_id)
            if not video:
                raise HTTPException(status_code=404, detail=f"Video {video_id} not found")

            cv = CourseVideoModel(
                course_id=course.id,
                video_id=video_id,
                order_index=idx,
            )
            await course_video_repo.create(cv)

    return await course_repo.get_with_videos(course.id)


@router.patch("/{course_id}", response_model=Course)
async def update_course(
    course_id: UUID,
    course_data: CourseUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update a course."""
    repo = CourseRepository(db)
    course = await repo.get_by_id(course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    update_data = course_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(course, key, value)

    await repo.save(course)
    return await repo.get_with_videos(course_id)


@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_course(
    course_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Delete a course."""
    repo = CourseRepository(db)
    course = await repo.get_by_id(course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    await repo.delete(course_id)


@router.post(
    "/{course_id}/videos/{video_id}",
    response_model=CourseVideo,
    status_code=status.HTTP_201_CREATED,
)
async def add_video_to_course(
    course_id: UUID,
    video_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Add a video to a course."""
    course_repo = CourseRepository(db)
    course = await course_repo.get_by_id(course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    video_repo = VideoRepository(db)
    video = await video_repo.get_by_id(video_id)
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    course_video_repo = CourseVideoRepository(db)
    existing = await course_video_repo.get_by_course_and_video(course_id, video_id)
    if existing:
        raise HTTPException(status_code=400, detail="Video already in course")

    course_videos = await course_video_repo.get_by_course_id(course_id)
    next_index = max((cv.order_index for cv in course_videos), default=-1) + 1

    from app.models.course import CourseVideo as CourseVideoModel

    cv = CourseVideoModel(
        course_id=course_id,
        video_id=video_id,
        order_index=next_index,
    )
    return await course_video_repo.create(cv)


@router.delete("/{course_id}/videos/{video_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_video_from_course(
    course_id: UUID,
    video_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Remove a video from a course."""
    course_video_repo = CourseVideoRepository(db)
    cv = await course_video_repo.get_by_course_and_video(course_id, video_id)
    if not cv:
        raise HTTPException(status_code=404, detail="Video not in course")

    await course_video_repo.delete(cv.id)


@router.put("/{course_id}/videos/reorder", response_model=Course)
async def reorder_videos(
    course_id: UUID,
    reorder_data: ReorderVideosRequest,
    db: AsyncSession = Depends(get_db),
):
    """Reorder videos in a course."""
    course_repo = CourseRepository(db)
    course = await course_repo.get_by_id(course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    course_video_repo = CourseVideoRepository(db)
    for video_id, new_index in reorder_data.video_orders.items():
        cv = await course_video_repo.get_by_course_and_video(course_id, video_id)
        if cv:
            cv.order_index = new_index
            await course_video_repo.save(cv)

    return await course_repo.get_with_videos(course_id)
