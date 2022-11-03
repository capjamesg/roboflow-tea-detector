import datetime
import json
import os
import time

import cv2
from roboflowoak import RoboflowOak

most_recent_time_found = None

coffee_breaks = []
coffee_break_ongoing = False

# number of seconds to wait for a mug to be away before a coffee break begins
DELAY = 4


def save_coffee_break_to_file(break_record: json) -> None:
    coffee_break_file_records = []

    if os.path.exists("coffee_breaks.json"):
        with open("coffee_breaks.json", "r") as f:
            coffee_break_file_records = json.load(f)

    with open("coffee_breaks.json", "w+") as f:
        coffee_break_file_records.append(break_record)
        json.dump(coffee_break_file_records, f)


def end_coffee_break() -> None:
    with open("coffee_breaks.json", "r") as f:
        coffee_break_file_records = json.load(f)
        coffee_break_file_records[-1]["is_ongoing"] = False
        coffee_break_file_records[-1]["end"] = str(current_time)
        duration = current_time - datetime.datetime.strptime(
            coffee_break_file_records[-1]["start"], "%Y-%m-%d %H:%M:%S.%f"
        )
        coffee_break_file_records[-1]["duration"] = duration.total_seconds()

    with open("coffee_breaks.json", "w+") as f:
        json.dump(coffee_break_file_records, f)


if __name__ == "__main__":
    # instantiating an object (rf) with the RoboflowOak module
    # API Key: https://docs.roboflow.com/rest-api#obtaining-your-api-key
    rf = RoboflowOak(
        model="cupdetection-gcltp",
        confidence=0.5,
        overlap=0.5,
        version="1",
        api_key=os.environ.get("ROBOFLOW_KEY"),
        rgb=True,
        depth=True,
        device=None,
        blocking=True,
    )
    # Running our model and displaying the video output with detections
    while True:
        t0 = time.time()
        # The rf.detect() function runs the model inference
        result, frame, raw_frame, depth = rf.detect()
        predictions = result["predictions"]

        # timing: for benchmarking purposes
        t = time.time() - t0

        # start a coffee break if the mug is away for more than DELAY seconds
        if (
            len(predictions) == 0
            and most_recent_time_found
            and most_recent_time_found
            < datetime.datetime.now() - datetime.timedelta(seconds=DELAY)
            and coffee_break_ongoing is False
        ):
            break_data = {
                "start": most_recent_time_found,
                "is_ongoing": True,
                "end": None,
                "duration": None,
            }

            coffee_breaks.append(break_data)

            print("Starting a coffee break...")
            coffee_break_ongoing = True
            break_data["start"] = str(break_data["start"])

            save_coffee_break_to_file(break_data)

        for p in predictions:
            result = p.json()

            if result["class"] == "cup":
                current_time = datetime.datetime.now()
                most_recent_time_found = current_time

            if result["confidence"] > 0.3 and coffee_break_ongoing is True:
                print("Ending a coffee break...")
                coffee_break_ongoing = False

                end_coffee_break()

        # displaying the video feed as successive frames
        cv2.imshow("frame", frame)

        # how to close the OAK inference window / stop inference: CTRL+q or CTRL+c
        if cv2.waitKey(1) == ord("q"):
            break
