from typing import List, Tuple
from os import remove
from librosa.core.convert import time_to_frames
from enum import Enum, IntEnum


class Index(IntEnum):
    LATIN_NAME = 0
    FILENAME = 1
    START_TIME = 2
    END_TIME = 3
    QUALITY_TAG = 4
    INDIVIDUAL_TAG = 5
    GROUP_ID = 6
    VOCALIZATION_TYPE = 7
    CHANNEL = 8


class Action(Enum):
    START = "start"
    END = "end"


class LabelAction:
    time: float
    type: Action
    index: int

    def __init__(
        self,
        time: float,
        type: Action,
        index: int,
    ):
        self.time = time
        self.type = type
        self.index = index


class LabeGeneratorBaseClass:
    annotations: List[list] = None
    min_length: -1

    def __init__(self, annotations: List[list]):
        """
        "latin_name","filename","start_time", "end_time","quality_tag","individual_id","group_id","quality_tag","channel",
        """
        self.annotations = annotations

    def create_label(
        selg, start: float, stop: float, annotations: List[LabelAction]
    ) -> None:
        """Return multi label of all annontations for this time interval """
        raise NotImplementedError

    def create_start_stop_list(
        self, annotations_of_file: List[list]
    ) -> List[LabelAction]:
        start_stop_list = []
        for index, annoation in enumerate(annotations_of_file, start=0):
            start_stop_list.append(
                LabelAction(annoation[Index.START_TIME], Action.START, index)
            )
            start_stop_list.append(
                LabelAction(annoation[Index.END_TIME], Action.END, index)
            )
        start_stop_list.sort(key=lambda x: x.time)
        return start_stop_list

    def create_raw_label_list(
        self,
        start_stop_list: List[Action],
    ) -> Tuple[float, float, List[list]]:
        labels_list: list[set] = []
        current_labels = set()
        last_action_time: float = None
        for action in start_stop_list:
            if action.type == Action.START:
                current_labels.add(action.index)
            else:
                current_labels.remove(action.index)
            if len(current_labels) > 0:
                if (
                    last_action_time is not None
                ):  # prevent adding only a start action after a pause
                    labels_list.append(
                        (last_action_time, action.time, current_labels.copy())
                    )
                last_action_time = (
                    action.time
                )  # set new start point for next label interval
            else:  # there is no bird label reset last_action_time in order to not label this pause of birdsongs
                last_action_time = None
        return labels_list

    def create_multi_labels(self) -> List[Tuple]:

        annotations = self.annotations
        filebased_annotations: list[list] = []
        last_filename: str = None
        tmp_group = []
        for annotation in annotations:
            if annotation[Index.FILENAME] != last_filename:
                if len(tmp_group) > 0:
                    filebased_annotations.append(tmp_group)
                    tmp_group = []
                last_filename = annotation[Index.FILENAME]
            tmp_group.append(annotation)
        if len(tmp_group) > 0:
            filebased_annotations.append(tmp_group)
        all_labels = []
        for annotations_of_file in filebased_annotations:

            start_stop_list = self.create_start_stop_list(annotations_of_file)
            raw_labels = self.create_raw_label_list(start_stop_list)

            labels_of_file = list(
                map(
                    lambda x: self.create_label(
                        x[0],
                        x[1],
                        list(map(lambda index: annotations_of_file[index], x[2])),
                    ),
                    raw_labels,
                )
            )
            all_labels += labels_of_file

        return all_labels

    def create_single_labels(self) -> List[Tuple]:
        annotations = self.annotations
        tmp_group = []
        for a in annotations:
            duration = a[Index.END_TIME] - a[Index.START_TIME]
            start = a[Index.START_TIME]
            stop = a[Index.END_TIME]
            label = a[Index.LATIN_NAME]
            filename = a[Index.FILENAME]
            tmp_group.append((duration, start, stop, label, 1, filename))
        return tmp_group


class SimpleMultiLabels(LabeGeneratorBaseClass):
    def create_label(self, start, stop, annotations):
        length = stop - start
        labels_list = list(set(map(lambda x: x[Index.LATIN_NAME], annotations)))
        labels = ",".join(labels_list)
        return (
            length,
            start,
            stop,
            labels,
            len(labels_list),
            annotations[0][Index.FILENAME],
        )
        annotations = self.annotations
