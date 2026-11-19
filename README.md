# On-Device AI (Flutter teaching app)

Take or pick a photo and the app tells you what's in it, entirely on the phone.
It uses TensorFlow Lite (LiteRT) image classifiers trained on ImageNet (1000 everyday objects and animals).
No internet connection or API key is needed.

## Features
- 📷 **Camera / Gallery**: classify any photo and see the top 3 answers with confidence bars and timing.
- 🧠 **Model switch** (chip icon): **EfficientNet-Lite4** is accurate (81.5% top-1, 15 MB). **MobileNet V1** is fast (≈70%, 4 MB).
- 🔁 **Retry**: run the same photo again, e.g. after switching model, to compare.
- 🕘 **History**: results are saved on the device. Tap to reopen, swipe to delete, or clear all.
- ✖️ **Clear**: reset the screen.

## Run
```
flutter pub get
flutter run --release   # full speed; use plain `flutter run` for hot reload
```
The iOS simulator has no camera, so use the **Gallery** button there.
**iOS on a real device:** set your Apple team so the app can be signed. The easiest way is to create `ios/Flutter/Signing.xcconfig` (git-ignored) containing:
```
DEVELOPMENT_TEAM = YOUR_TEAM_ID
```
You can find your team ID in Xcode → Settings → Accounts, or at developer.apple.com → Membership.
Alternatively, open `ios/Runner.xcworkspace` in Xcode and choose your team under Signing & Capabilities, but don't commit that change.

## Where to look
| File | What it teaches |
|---|---|
| `lib/services/classifier.dart` | **All the AI code** in 4 steps: Load → Preprocess → Run → Postprocess. Reads input size and type from the model. |
| `lib/models/model_config.dart` | The list of models. Add yours here. |
| `lib/services/history_store.dart` | Saving results and photos to the device |
| `lib/screens/` | UI: home (camera, results, Retry, Clear) and history |
| `assets/models/` | `.tflite` model files and their label lists |
| `docs/OnDevice_AI_Class_Handbook.pdf` | **Class handbook:** how LLMs work, training your own model, hosting models online, lesson plan |
| `docs/make_pdf.py` | Regenerates the handbook: `python3 docs/make_pdf.py docs/OnDevice_AI_Class_Handbook.pdf` (needs `reportlab`) |

## Add your own model
1. Train one with Teachable Machine (choose the *Quantized* TFLite export) or Keras (see section 4 of the handbook).
2. Copy the `.tflite` and labels file into `assets/models/` and list them in `pubspec.yaml`.
3. Add a `ModelConfig` in `lib/models/model_config.dart`. It will appear in the model menu.

## Setup notes (already done)
- Android: `minSdk = 26`. `android/build.gradle.kts` aligns the tflite_flutter plugin's Kotlin JVM target.
- iOS: camera and photo-library permission strings are in `ios/Runner/Info.plist`.

## Credits
The models are Google's [EfficientNet-Lite](https://github.com/tensorflow/tpu/tree/master/models/official/efficientnet/lite) and [MobileNet V1](https://www.tensorflow.org/lite/models) (Apache 2.0). Both are trained on ImageNet.
