#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys


KEEP_SENTINEL = "__OPENCLAW_KEEP__"
CLEAR_SENTINEL = "__OPENCLAW_CLEAR__"
FIELD_DELIMITER = "\x1f"


CREATE_SCRIPT = r'''
on joinFields(fieldList)
	set previousDelimiters to AppleScript's text item delimiters
	set AppleScript's text item delimiters to character id 31
	set joinedText to fieldList as text
	set AppleScript's text item delimiters to previousDelimiters
	return joinedText
end joinFields

on run argv
	set titleText to item 1 of argv
	set noteText to item 2 of argv
	set listName to item 3 of argv
	set yearNum to (item 4 of argv) as integer
	set monthNum to (item 5 of argv) as integer
	set dayNum to (item 6 of argv) as integer
	set hourNum to (item 7 of argv) as integer
	set minuteNum to (item 8 of argv) as integer

	set monthNames to {January, February, March, April, May, June, July, August, September, October, November, December}

	tell application "Reminders"
		set theAccount to default account
		if listName is "" then
			set targetList to default list of theAccount
		else
			if not (exists list listName of theAccount) then error "Reminder list not found: " & listName
			set targetList to list listName of theAccount
		end if

		set dueDateValue to current date
		set year of dueDateValue to yearNum
		set month of dueDateValue to item monthNum of monthNames
		set day of dueDateValue to dayNum
		set time of dueDateValue to (hourNum * 3600 + minuteNum * 60)

		set reminderProps to {name:titleText, due date:dueDateValue}
		if noteText is not "" then set reminderProps to reminderProps & {body:noteText}

		tell targetList
			set createdReminder to make new reminder with properties reminderProps
		end tell

		set savedDueDate to due date of createdReminder
		return my joinFields({id of createdReminder, name of createdReminder, name of targetList, (year of savedDueDate) as text, (month of savedDueDate as integer) as text, (day of savedDueDate) as text, (hours of savedDueDate) as text, (minutes of savedDueDate) as text})
	end tell
end run
'''


UPDATE_SCRIPT = r'''
on joinFields(fieldList)
	set previousDelimiters to AppleScript's text item delimiters
	set AppleScript's text item delimiters to character id 31
	set joinedText to fieldList as text
	set AppleScript's text item delimiters to previousDelimiters
	return joinedText
end joinFields

on run argv
	set reminderId to item 1 of argv
	set targetListName to item 2 of argv
	set titleText to item 3 of argv
	set noteMode to item 4 of argv
	set yearNum to (item 5 of argv) as integer
	set monthNum to (item 6 of argv) as integer
	set dayNum to (item 7 of argv) as integer
	set hourNum to (item 8 of argv) as integer
	set minuteNum to (item 9 of argv) as integer

	set monthNames to {January, February, March, April, May, June, July, August, September, October, November, December}

	tell application "Reminders"
		set theAccount to default account
		set targetList to list targetListName of theAccount
		set targetReminder to first reminder of targetList whose id is reminderId

		set dueDateValue to current date
		set year of dueDateValue to yearNum
		set month of dueDateValue to item monthNum of monthNames
		set day of dueDateValue to dayNum
		set time of dueDateValue to (hourNum * 3600 + minuteNum * 60)

		if titleText is not "__OPENCLAW_KEEP__" then set name of targetReminder to titleText
		if noteMode is "__OPENCLAW_CLEAR__" then
			set body of targetReminder to ""
		else if noteMode is not "__OPENCLAW_KEEP__" then
			set body of targetReminder to noteMode
		end if
		set due date of targetReminder to dueDateValue

		set savedDueDate to due date of targetReminder
		return my joinFields({id of targetReminder, name of targetReminder, name of targetList, (year of savedDueDate) as text, (month of savedDueDate as integer) as text, (day of savedDueDate) as text, (hours of savedDueDate) as text, (minutes of savedDueDate) as text})
	end tell
end run
'''


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Create or update an Apple Reminder using AppleScript with explicit numeric "
            "date fields, then verify the saved reminder."
        )
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    create_parser = subparsers.add_parser("create", help="Create a reminder and verify it")
    create_parser.add_argument("--title", required=True)
    create_parser.add_argument("--notes", default="")
    create_parser.add_argument("--list", default="")
    add_due_args(create_parser)

    update_parser = subparsers.add_parser("update", help="Update a reminder by id and verify it")
    update_parser.add_argument("--reminder-id", required=True)
    update_parser.add_argument("--list", required=True)
    update_parser.add_argument("--title")
    update_parser.add_argument("--notes")
    update_parser.add_argument("--clear-notes", action="store_true")
    add_due_args(update_parser)

    return parser


def add_due_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--year", type=int, required=True)
    parser.add_argument("--month", type=int, required=True)
    parser.add_argument("--day", type=int, required=True)
    parser.add_argument("--hour", type=int, required=True)
    parser.add_argument("--minute", type=int, required=True)


def run_osascript(script: str, *args: str) -> str:
    proc = subprocess.run(
        ["osascript", "-", *args],
        input=script,
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        stderr = proc.stderr.strip() or proc.stdout.strip() or "osascript failed"
        raise RuntimeError(stderr)
    return proc.stdout.strip()


def validate_args(args: argparse.Namespace) -> None:
    if not 1 <= args.month <= 12:
        raise ValueError("--month must be between 1 and 12")
    if not 1 <= args.day <= 31:
        raise ValueError("--day must be between 1 and 31")
    if not 0 <= args.hour <= 23:
        raise ValueError("--hour must be between 0 and 23")
    if not 0 <= args.minute <= 59:
        raise ValueError("--minute must be between 0 and 59")


def apple_id(reminder_id: str) -> str:
    raw_id = reminder_id.removeprefix("x-apple-reminder://")
    return f"x-apple-reminder://{raw_id}"


def parse_verified_output(raw_output: str) -> dict[str, object]:
    parts = raw_output.split(FIELD_DELIMITER)
    if len(parts) != 8:
        raise RuntimeError(f"Unexpected AppleScript output: {raw_output}")
    return {
        "reminder_id": parts[0].removeprefix("x-apple-reminder://"),
        "title": parts[1],
        "list": parts[2],
        "year": int(parts[3]),
        "month": int(parts[4]),
        "day": int(parts[5]),
        "hour": int(parts[6]),
        "minute": int(parts[7]),
    }


def verify_result(actual: dict[str, object], expected: tuple[int, int, int, int, int]) -> dict[str, object]:
    expected_map = {
        "year": expected[0],
        "month": expected[1],
        "day": expected[2],
        "hour": expected[3],
        "minute": expected[4],
    }
    mismatches = {
        key: {"expected": expected_map[key], "actual": actual[key]}
        for key in expected_map
        if actual[key] != expected_map[key]
    }
    if mismatches:
        raise RuntimeError(
            "Reminder verification failed: "
            + json.dumps({"reminder_id": actual["reminder_id"], "mismatches": mismatches}, ensure_ascii=False)
        )

    actual["verified"] = True
    actual["due_iso_local"] = (
        f'{actual["year"]:04d}-{actual["month"]:02d}-{actual["day"]:02d}'
        f'T{actual["hour"]:02d}:{actual["minute"]:02d}'
    )
    return actual


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    try:
        validate_args(args)

        if args.command == "create":
            raw_output = run_osascript(
                CREATE_SCRIPT,
                args.title,
                args.notes,
                args.list,
                str(args.year),
                str(args.month),
                str(args.day),
                str(args.hour),
                str(args.minute),
            )
            result = parse_verified_output(raw_output)
            result = verify_result(result, (args.year, args.month, args.day, args.hour, args.minute))
            result["mode"] = "create"
        else:
            title_arg = args.title if args.title is not None else KEEP_SENTINEL
            if args.clear_notes:
                note_arg = CLEAR_SENTINEL
            elif args.notes is not None:
                note_arg = args.notes
            else:
                note_arg = KEEP_SENTINEL

            raw_output = run_osascript(
                UPDATE_SCRIPT,
                apple_id(args.reminder_id),
                args.list,
                title_arg,
                note_arg,
                str(args.year),
                str(args.month),
                str(args.day),
                str(args.hour),
                str(args.minute),
            )
            result = parse_verified_output(raw_output)
            result = verify_result(result, (args.year, args.month, args.day, args.hour, args.minute))
            result["mode"] = "update"

        print(json.dumps(result, ensure_ascii=False))
        return 0
    except Exception as exc:  # noqa: BLE001
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
