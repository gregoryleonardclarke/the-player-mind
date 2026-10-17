# The Player Mind — AI-assisted gaming psychology video studio

**Status:** Daily generation and review automation configured. **Publishing always requires explicit human approval for each video.** Never connect an automated publication step to the render workflow.

## How one daily video is made

1. The ChatGPT task **The Player Mind Daily Video** (approximately 8am UK time) checks existing topics and primary research, chooses a relevant real Full HD game clip from [the curated footage catalogue](assets/gameplay_catalog.json), and writes a researched 90–120-second lesson to the [briefs directory](briefs).
2. Creating a brief triggers [Daily Video Review](.github/workflows/daily-video-review.yml) in GitHub Actions. It downloads genuine original Full HD gameplay from the verified catalogue, cuts it to a 9:16 vertical video, adds large animated/timed captions and original chill music.
3. If and only if the video renders and passes file-level QA, Actions uploads a **downloadable MP4 review artifact** and opens a GitHub **Issue assigned to the repository owner**, with the preview link. Nothing is sent to TikTok, YouTube, Instagram or Buffer.
4. An additional ChatGPT review-watch task looks for new successful review requests and can remind the user. ChatGPT and GitHub notification preferences must be enabled if push/email notifications are desired.
5. The user watches the video and either asks for changes or explicitly approves **that specific video**. Only then can ChatGPT post it through the connected Buffer channels, with checked descriptions and the full-resolution video. Approval never carries over to later videos.

## Running manually

In GitHub, open **Actions → The Player Mind — Daily review video** and select **Run workflow**. It renders the latest JSON in briefs/ but does not publish.

Watch the output under **Actions → latest successful run → Artifacts → player-mind-review-1080p**. For an easier review link, open the most recent **Issues → Video ready for approval** issue.

**Preview artifacts expire after 7 days.** Review within that period, or rerun the workflow.

## Content format

Each JSON in briefs/ must contain:
- A title, duration (70–121 seconds) and a psychological lesson with consecutive timecoded caption cards
- Genuine research with real references and links
- One or more gameplay source IDs from assets/gameplay_catalog.json, matched to the game and topic
- YouTube title and social caption; no episode numbers, no generic "dopamine hacks"
- The explicit flag publish: false

The example [Fallout 4 autonomy mini-lesson](briefs/2026-10-17-rpg-choices.json) demonstrates the format. It is a test preview and has **not been published**.

The renderer enforces original gameplay at **at least 1920x1080 source resolution**; output is **1080x1920** MP4 with a real audio stream. If a source is unavailable or low-resolution, the run fails rather than inventing replacement footage.

## Operational limitations and notifications

The ChatGPT scheduled research task's first automatic write is not proven until its next scheduled run. The GitHub research-brief-to-video pipeline has been tested successfully with the Fallout 4 brief.

For notifications, open [GitHub Notifications settings](https://github.com/settings/notifications), enable notifications for **issues you're assigned to**, and allow email/mobile notifications as desired. Check ChatGPT's **Settings → Notifications** for the separate daily video review task; these were found disabled at setup.

The free source catalogue is finite. Some games lack verified HD recordings and cannot be produced automatically yet; more sources need checking and adding. GitHub Actions runtime and stored artifacts remain subject to GitHub policies and limits.

## Security

No Buffer tokens are saved in GitHub. GitHub uses its ephemeral Actions token only for creating the review issue and uploading the review artifact. The rendering workflow deliberately has no Buffer API upload or publication permission. The review issue and research text are visible in this public repository; the Actions artifact download may require GitHub authentication.
