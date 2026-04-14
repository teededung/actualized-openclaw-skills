---
name: apple-reminders
version: "1.1.0"
description: Use when creating or updating Apple Reminders on macOS that should sync to iPhone and keep audible notification alarms, especially when dates must be interpreted by country or locale.
read_when:
  - User asks to create an Apple Reminder on macOS with a due date and wants reminder notifications to work on Apple devices.
  - User gives a slash-form, country-specific, locale-specific, Vietnamese, or day-first date such as `9/3`, `09/03/2026`, or `ngày 9 tháng 3`.
  - User asks to change the due date or time of an existing reminder and the saved value must be verified after writing.
  - User explicitly mentions Apple Reminders, Reminders.app, or wants to avoid the `remindctl add` no-notification limitation.
metadata:
  openclaw:
    homepage: https://support.apple.com/guide/reminders/welcome/mac
    emoji: "🔔"
    requires:
      bins: [python3, osascript]
---

# Apple Reminders

Use this skill for reminder creation and due-date changes that must keep Apple notification behavior. The bundled script writes reminders with AppleScript using explicit numeric `year/month/day/hour/minute` fields, then reads the saved reminder back inside AppleScript and fails if the stored values do not match.

## Install Note

- Install this skill only on macOS.
- It writes to Reminders.app through AppleScript.
- Reminders can sync to iPhone through iCloud Reminders when both devices use the same Apple ID and Reminders sync is enabled.
- Use this skill when the reminder needs a working notification alarm or sound.

## Tool Selection

| Goal | Recommended Tool | Reason |
| --- | --- | --- |
| List, inspect, delete, complete | `remindctl` | Fast CLI, structured output, good for JSON |
| Create a reminder that must notify | Bundled script / AppleScript | `remindctl add` creates the reminder but does not create a working alarm |
| Change a due date or time that must notify | Bundled script / AppleScript | Preserve notification behavior and verify the saved value |

## Hard Rules

- Use AppleScript for create and due-date update operations.
- Do not use `remindctl add` for reminders that must notify on macOS or iPhone.
- Do not use `remindctl edit` for due-date or due-time updates that must preserve notifications.
- Never pass raw slash-form dates into AppleScript.
- Normalize the user's date intent into numeric fields before running the script.
- If the user wants a notification but does not give a time, ask for the time instead of guessing.
- If writing raw AppleScript instead of the bundled script, treat AppleScript date parsing as `MM/DD/YYYY` and prefer explicit month names or separately assigned numeric fields.

## Locale Date Policy

Interpret slash-form dates using the user's explicit country, locale, or language context before converting to numeric fields for the script.

| Context | Interpret `5/3/2026` as |
| --- | --- |
| Vietnam, Vietnamese, UK, EU, Australia, or explicit day-first | 5 March 2026 |
| US or explicit month-first | May 3, 2026 |
| ISO date `2026-03-05` | 5 March 2026 |

Rules:

- Vietnamese phrasing such as `ngày 5 tháng 3` is always day `5`, month `3`.
- If the country, locale, or language clearly implies a date order, use that order.
- If a slash-form date has both numbers `<= 12` and no country, locale, language, or explicit format is clear, ask before writing.
- If one number is `> 12`, infer the only valid date order.
- Never pass raw slash-form dates into AppleScript.

## Commands

### Create a reminder

```bash
python3 {baseDir}/scripts/create_or_update_reminder.py create \
  --title "Họp online" \
  --list "Reminders" \
  --year 2026 \
  --month 3 \
  --day 9 \
  --hour 14 \
  --minute 30
```

### Update an existing reminder

For updates, identify the exact reminder and its list first, then update by stable `id`.

```bash
python3 {baseDir}/scripts/create_or_update_reminder.py update \
  --reminder-id "x-apple-reminder://..." \
  --list "Reminders" \
  --year 2026 \
  --month 3 \
  --day 9 \
  --hour 14 \
  --minute 30
```

## Working Method

1. Normalize the user request into numeric fields.

- Apply the Locale Date Policy for slash-form and country-specific dates.
- Treat Vietnamese phrasing such as `ngày 9 tháng 3` as day `9`, month `3`.
- Confirm the year when it is missing and the intended year is not obvious.

2. Write with AppleScript.

- The script sets `year`, `month`, `day`, and `time` separately.
- This avoids AppleScript locale parsing mistakes such as swapping March 9 and September 3.
- If you must write raw AppleScript, set `time of myDate` to seconds from midnight, for example `14 * 3600 + 50 * 60` for 14:50.

3. Verify before reporting success.

- The script reads back the created or updated reminder inside AppleScript.
- It exits non-zero if year, month, day, hour, or minute does not match.
- Only report success after the verification output succeeds.

## Read-Only Lookup

If you need to find an existing reminder before updating it, you may use `remindctl` or AppleScript for read-only inspection. Do not use `remindctl add` or `remindctl edit` for the notification-carrying write path.

## Output Discipline

- Confirm the saved reminder using exact numbers, for example `2026-03-09 14:30`.
- If verification fails, show the mismatch and fix it instead of claiming success.
