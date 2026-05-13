from pydantic import BaseModel

class AcademicSummary(BaseModel):
    total_students: int
    total_classes: int
    total_sections: int
    total_subjects: int
    total_enrollments: int

class ExamSummary(BaseModel):
    total_exam_types: int
    total_marks_entered: int
    total_results_computed: int
