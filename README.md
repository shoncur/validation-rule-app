# validation-rule-app
This application will be able to verify that all bases are covered when uploading a CO to Arena.

> Reminder that we are trying to do all DOCUMENT change orders, not PART change orders
> Does CMDC have a WRK for change orders?

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
      > Note from Trish: UoM "DOC or N/A" is indicated
      - Always goes to rev A
      - Everything has checkmarks (does this need to change? Checkmarks are not accurate for initial release)
      > Any attributes that has a yellow dot requires a check box and will always include the files attribute
      - PDF is the primary file (needs a primary file)
      - If RETRAINED then quiz needs to be in implementation
      > Sometimes they do not attach them in the correct place. So if this could be "..found in to the impl. or files of the CO." make sure it is on the most current template (DOT)
    - Document/File Update
      > Needs an Impact Assessment <br>
      > Make sure that it is not "In Production" but yet "Production Release" <br>
      > UoM "DOC or N/A" is indicated
      > Revises to the next Rev
      - Everything has checkmarks (does this need to change? Checkmarks are not accurate for initial release)
      > Any attributes that has a yellow dot requires a check box and will always include the files attribute
      - Check the categories ensure that redlines are included in the files
      > Make sure it is on the most current template (DOT)
      - If RETRAINED then quiz needs to be in implementation
      > Sometimes they do not attach them in the correct place. So if this could be "..found in to the impl. or files of the CO." make sure it is on the most current template (DOT)
    - Part Update
      - ...
    - BOM Update
      - ...
    - Supplier Update
      - ...
    - Lifecycle Update
      - Ensure that old lifecycle phase existed so the item is not in initial release
      - Check that new lifecycle phase is different from old lifecycle phase
      > Lifecycle phase will stay the same if revising. Something that is in Production Release will stay in the same lifecycle phase unless it is INA or OBS
      > Should never be in "In Production" lifecycle phase

Notes on acronyms:
UoM = Unit of Measure
INA = Inactive
OBS = Obselete
