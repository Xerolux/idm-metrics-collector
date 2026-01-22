"""
Annotations Management for Dashboards

Allows users to add time-based markers/annotations to charts
(e.g., "Wartung am 15.1.", "Filter gewechselt", "Fehler behoben")
"""

from datetime import datetime
from typing import List, Dict, Optional
import json


class Annotation:
    """Represents a single annotation"""

    def __init__(self, annotation_id: str, time: int, text: str, tags: List[str] = None,
                 color: str = '#ef4444', dashboard_id: Optional[str] = None):
        self.id = annotation_id
        self.time = time  # Unix timestamp
        self.text = text
        self.tags = tags or []
        self.color = color
        self.dashboard_id = dashboard_id

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'time': self.time,
            'text': self.text,
            'tags': self.tags,
            'color': self.color,
            'dashboard_id': self.dashboard_id
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Annotation':
        """Create from dictionary"""
        return cls(
            annotation_id=data.get('id'),
            time=data.get('time', int(datetime.now().timestamp())),
            text=data.get('text', ''),
            tags=data.get('tags', []),
            color=data.get('color', '#ef4444'),
            dashboard_id=data.get('dashboard_id')
        )


class AnnotationManager:
    """Manages annotations for dashboards"""

    def __init__(self, config):
        self.config = config
        self.annotations_file = 'annotations.json'

    def get_all_annotations(self) -> List[Annotation]:
        """Get all annotations"""
        data = self.config.data.get('annotations', [])
        return [Annotation.from_dict(a) for a in data]

    def get_annotations_for_dashboard(self, dashboard_id: str) -> List[Annotation]:
        """Get annotations for a specific dashboard"""
        all_annotations = self.get_all_annotations()
        return [a for a in all_annotations if a.dashboard_id == dashboard_id or a.dashboard_id is None]

    def get_annotations_for_time_range(self, start: int, end: int, dashboard_id: str = None) -> List[Annotation]:
        """Get annotations within a time range"""
        annotations = self.get_all_annotations()

        if dashboard_id:
            annotations = [a for a in annotations if a.dashboard_id == dashboard_id or a.dashboard_id is None]

        return [a for a in annotations if start <= a.time <= end]

    def add_annotation(self, time: int, text: str, tags: List[str] = None,
                      color: str = '#ef4444', dashboard_id: str = None) -> Annotation:
        """Add a new annotation"""
        import uuid
        annotation_id = str(uuid.uuid4())

        annotation = Annotation(
            annotation_id=annotation_id,
            time=time,
            text=text,
            tags=tags or [],
            color=color,
            dashboard_id=dashboard_id
        )

        if 'annotations' not in self.config.data:
            self.config.data['annotations'] = []

        self.config.data['annotations'].append(annotation.to_dict())
        self.config.save()

        return annotation

    def update_annotation(self, annotation_id: str, time: int = None, text: str = None,
                         tags: List[str] = None, color: str = None) -> Optional[Annotation]:
        """Update an existing annotation"""
        annotations = self.config.data.get('annotations', [])

        for i, ann in enumerate(annotations):
            if ann['id'] == annotation_id:
                if time is not None:
                    ann['time'] = time
                if text is not None:
                    ann['text'] = text
                if tags is not None:
                    ann['tags'] = tags
                if color is not None:
                    ann['color'] = color

                self.config.data['annotations'][i] = ann
                self.config.save()
                return Annotation.from_dict(ann)

        return None

    def delete_annotation(self, annotation_id: str) -> bool:
        """Delete an annotation"""
        annotations = self.config.data.get('annotations', [])

        for i, ann in enumerate(annotations):
            if ann['id'] == annotation_id:
                del self.config.data['annotations'][i]
                self.config.save()
                return True

        return False

    def get_annotation(self, annotation_id: str) -> Optional[Annotation]:
        """Get a specific annotation by ID"""
        annotations = self.get_all_annotations()
        for annotation in annotations:
            if annotation.id == annotation_id:
                return annotation
        return None
