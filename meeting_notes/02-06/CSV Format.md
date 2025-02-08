**All items in bold must have a value**

**`docNo`** - document number (possible generated at runtime)
**`time`** - [UNIX timestamp](https://en.wikipedia.org/wiki/Unix_time) of the message
**`sender`** - the *name* of the sender
**`message`** - the message content. if non-text (e.g. photo) please mention this in some way (e.g. "*Photo*"). Refer below for OCR information
**`isReply`** - boolean, defaults to `False` if the message is not a reply
`who_replied_to` - the `docNo` that the message is a reply to.
**`has_reactions`** - boolean, defaults to `False` if the message has no reactions attatched
`reactions` - an array of reactions in the format `[user: {reaction}, user: {reaction}, ...]`
**`translated`** - boolean, defaults to `False` if the message has not been translated into another language
**`is_media`** - boolean, defaults to `False` if the message is just text
**`is_OCR`** - booleandefaults to `False` if the message has been OCR'd (and the `message` field is the result of this OCR'ing)
`local_uri` - the local filepath to the image (if available)
`remote_url` - the url to the media stored on the server