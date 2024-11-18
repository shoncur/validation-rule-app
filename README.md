# validation-rule-app
This application will be able to verify that all bases are covered when uploading a CO to Arena.

## How does this app work?
Here is the general process that the application undergoes:

- Launch application
- Show login popup
- After logging in, show main app
- Enter CO # and click 'validate'
  - validate_clicked() is called and will clear the display
  - validate_clicked() will call Arena and check if the CO is a valid number
    - if CO not valid, error
    - if CO valid, get type of change
      - if type of change valid, call dispatch_process()
      - if type of change not valid, error
  - dispatch_process() will call the correct method for the type of change
    - Initial Release checks for the following:
      - Get sourcing (DOCUMENT types do not require sourcing)
        - Search the number in items world
        - Check if it is a document or not (use the document_prefixes.txt file to check prefixes)
      - Documents go from unreleased to production release
      - Always goes to rev A
      - Everything has checkmarks (does this need to change? Checkmarks are not accurate for initial release)
      - PDF is the primary file (needs a primary file)
      - If RETRAINED then quiz needs to be in implementation
    - Document Update
      - Check the categories ensure that redlines are included in the files
    - Lifecycle Update
      - Ensure that old lifecycle phase existed so the item is not in initial release
      - Check that new lifecycle phase is different from old lifecycle phase