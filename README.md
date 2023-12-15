# Novel Scraping To-Do List

## Task 1: Fetch Novel Page URL
- [ ] Action: Retrieve the novel page URL from the user.
- [ ] Command: `<<get_novel_page_url=https://sangtacviet.vip/truyen/sangtac/1/17488/`
- [ ] Validation: `::validate_novel_page_url`

## Task 2: Get Title from the Novel Page
- [ ] Action: Extract the title from the novel page.
- [ ] Command: `<<get_title=novel, from the novel page`
- [ ] Translation: `<<translate_the_title_into_english`

## Task 3: Create Folder for the Novel
- [ ] Action: Create a folder with the novel title if it doesn't exist.
- [ ] Command: `<<create_folder_with_title` (conditional on non-existence)

## Task 4: Get Chapter List from the Novel Page
- [ ] Action: Retrieve the list of chapters from the novel page.
- [ ] Command: `>>get_chapter_list_from_the_novel_page`

## Task 5: Start Scraping Chapters
- [ ] Action: Determine the starting chapter to be scraped.
- [ ] Command: `<<get_start_of=chapter=>to_be scraped()`
- [ ] Error Check: `<<check if the user entered len(chapters) > starting_chap>> (throw error if true)`

## Task 6: Scraping Loop
- [ ] Loop Start: `<<start i from the starting_of_user_entered_chapter_num>>`
  - [ ] Sub-Task 1: Go to the Chapter Page: `<<go_to_chap_page>>`
  - [ ] Sub-Task 2: Translate the Chapter into English: `<<translate_the_chap_into_eng>>`
  - [ ] Sub-Task 3: Save to the Novel Folder: `<<save_to_the_novel_folder(user_specified_download_folder/novel_folder/chap_num.txt)=if doesn't exist>> (modify if scraped content)`
- [ ] Loop End: `<<done>>`

## Completion
- [ ] Action: Display completion message.