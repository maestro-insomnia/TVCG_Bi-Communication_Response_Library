# Audio Files Are Not Distributed

The prerecorded audio used in the original experiment is **not included in this repository because the recordings cannot be redistributed under the applicable copyright/licensing constraints**.

The repository therefore provides only response text, response codes, action codes, and expected local filenames. Researchers who reuse the protocol should create their own recordings and document their recording/processing procedure.

Recommended local layout:

```text
audio/
├── opening/BC_OPENING.wav
├── broad/BC_BRD01_PREFERRED.wav
├── broad/BC_BRD01_ALTERNATIVE.wav
├── ...
├── specific/BC_SPC01_SHIRT_TYPE.wav
├── ...
├── decision/BC_DEC01_HOODIE.wav
├── decision/BC_DEC02_SHIRT.wav
└── control/BC_CTL01_ONE_QUESTION.wav
    ...
    control/BC_CTL07_CONTINUE_ASKING.wav
```

Use `audio_manifest.example.csv` as the mapping template. Common audio extensions are excluded by the repository `.gitignore` to reduce the chance of accidental redistribution.
