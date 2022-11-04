import datetime
import json
import os
import time

import cv2
from roboflowoak import RoboflowOak
from slack_sdk import WebClient

DELAY = 60
ACTIVE_RECORD = {
    "status_text": "making tea",
    "status_emoji": ":teapot:",
    "status_expiration": 0
}

inactive_record = {
    "status_text": "",
    "status_emoji": "",
    "status_expiration": 0
}

if os.environ.get("ROBOFLOW_KEY") is None:
    raise Exception("Please specify a ROBOFLOW_KEY environment variable with your Roboflow API key.")

if os.environ.get("SLACK_KEY"):
    client = WebClient(token=os.environ.get("SLACK_KEY"))
else:
    client = None


def save_tea_break_to_file(break_record: dict) -> None:
    """
    Save a record of a tea break to the tea_breaks.json file.

    Parameters
    ----------

    break_record: dict
        A dictionary with information about a tea break.
    """
    tea_break_file_records = []

    if os.path.exists("tea_breaks.json"):
        with open("tea_breaks.json", "r") as f:
            tea_break_file_records = json.load(f)

    with open("tea_breaks.json", "w+") as f:
        tea_break_file_records.append(break_record)
        json.dump(tea_break_file_records, f)

    if client is not None:
        try:
            client.users_profile_set(profile=ACTIVE_RECORD)
        except Exception as e:
            print(e)


def end_tea_break() -> None:
    """
    Update the most recent tea break record to reflect the break has ended.
    """
    with open("tea_breaks.json", "r") as f:
        current_time = datetime.datetime.now()
        tea_break_file_records = json.load(f)
        tea_break_file_records[-1]["is_ongoing"] = False
        tea_break_file_records[-1]["end"] = str(current_time)
        duration = current_time - datetime.datetime.strptime(
            tea_break_file_records[-1]["start"], "%Y-%m-%d %H:%M:%S.%f"
        )
        tea_break_file_records[-1]["duration"] = duration.total_seconds()

    with open("tea_breaks.json", "w+") as f:
        json.dump(tea_break_file_records, f)

    if client is not None:
        try:
            client.users_profile_set(profile=inactive_record)
        except Exception as e:
            print(e)


def main():
    """
    Run the mug detector model.
    """
    most_recent_time_found = None
    tea_break_ongoing = False

    # instantiating an object (rf) with the RoboflowOak module
    # API Key: https://docs.roboflow.com/rest-api#obtaining-your-api-key
    rf = RoboflowOak(model="mug-detector-0akq7", confidence=0.5, overlap=0.5,
    version="4", api_key=os.environ.get("ROBOFLOW_KEY"), rgb=True,
    depth=True, device=None, blocking=True)
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
            and tea_break_ongoing is False
        ):
            break_data = {
                "start": most_recent_time_found,
                "is_ongoing": True,
                "end": None,
                "duration": None,
            }

            print("Starting a coffee break...")

            tea_break_ongoing = True
            break_data["start"] = str(break_data["start"])

            save_tea_break_to_file(break_data)

        for p in predictions:
            result = p.json()

            if result["class"] == "cup":
                current_time = datetime.datetime.now()
                most_recent_time_found = current_time

            if result["confidence"] > 0.3 and tea_break_ongoing is True:
                print("Ending a tea break...")
                tea_break_ongoing = False

                end_tea_break()

        # displaying the video feed as successive frames
        # cv2.imshow("frame", frame)

        # how to close the OAK inference window / stop inference: CTRL+q or CTRL+c
        if cv2.waitKey(1) == ord("q"):
            print("Ending a tea break...")
            end_tea_break()
            break


if __name__ == "__main__":
    main()
