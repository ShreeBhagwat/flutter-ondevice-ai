import sys
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, PageBreak, CondPageBreak, Table,
                                TableStyle, Preformatted, KeepTogether, ListFlowable, ListItem)
from reportlab.graphics.shapes import Drawing, Rect, String, Line, Polygon

OUT = sys.argv[1]
INK = colors.HexColor("#1f2340")
ACC = colors.HexColor("#3f51b5")
SOFT = colors.HexColor("#eef0fb")
CODEBG = colors.HexColor("#f5f5f7")
MUTED = colors.HexColor("#5b5f73")

ss = getSampleStyleSheet()
H1 = ParagraphStyle("H1", parent=ss["Heading1"], textColor=ACC, fontSize=20, leading=24, spaceBefore=4, spaceAfter=10)
H2 = ParagraphStyle("H2", parent=ss["Heading2"], textColor=INK, fontSize=14, leading=18, spaceBefore=12, spaceAfter=6, keepWithNext=1)
B = ParagraphStyle("B", parent=ss["BodyText"], fontSize=10.5, leading=15, textColor=INK, spaceAfter=6)
SM = ParagraphStyle("SM", parent=B, fontSize=9, leading=12, textColor=MUTED)
CODE = ParagraphStyle("CODE", fontName="Courier", fontSize=8.3, leading=10.6, textColor=INK)
TIP = ParagraphStyle("TIP", parent=B, fontSize=10, leading=14)


def p(t, s=B): return Paragraph(t, s)


def bullets(items):
    return ListFlowable([ListItem(p(i), leftIndent=12) for i in items],
                        bulletType="bullet", start="•", leftIndent=14, bulletFontSize=9)


def code(src):
    t = Table([[Preformatted(src.strip("\n"), CODE)]], colWidths=[170 * mm])
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), CODEBG),
                           ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#d8d8e0")),
                           ("LEFTPADDING", (0, 0), (-1, -1), 8), ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                           ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]))
    return t


def tip(title, text):
    t = Table([[p(f"<b>{title}</b><br/>{text}", TIP)]], colWidths=[170 * mm])
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), SOFT),
                           ("LINEBEFORE", (0, 0), (0, -1), 3, ACC),
                           ("LEFTPADDING", (0, 0), (-1, -1), 10), ("TOPPADDING", (0, 0), (-1, -1), 7),
                           ("BOTTOMPADDING", (0, 0), (-1, -1), 7)]))
    return t


def table(rows, widths):
    data = [[p(f"<b>{c}</b>" if r == 0 else c, SM if r else B) for c in row] for r, row in enumerate(rows)]
    t = Table(data, colWidths=[w * mm for w in widths], repeatRows=1)
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), SOFT),
                           ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#c9cbe0")),
                           ("VALIGN", (0, 0), (-1, -1), "TOP"),
                           ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5)]))
    return t


def flow(labels, width=170 * mm, h=46, sub=None):
    """Horizontal box -> box -> box diagram."""
    n = len(labels)
    gap = 14
    bw = (width - gap * (n - 1)) / n
    d = Drawing(width, h + (14 if sub else 0))
    y0 = 14 if sub else 0
    for i, lab in enumerate(labels):
        x = i * (bw + gap)
        d.add(Rect(x, y0, bw, h, rx=6, ry=6, fillColor=SOFT, strokeColor=ACC, strokeWidth=1))
        lines = lab.split("\n")
        for j, ln in enumerate(lines):
            yy = y0 + h / 2 + (len(lines) / 2 - j - 0.8) * 11
            d.add(String(x + bw / 2, yy, ln, fontName="Helvetica-Bold" if j == 0 else "Helvetica",
                         fontSize=8.5 if j == 0 else 7.5, fillColor=INK, textAnchor="middle"))
        if sub:
            d.add(String(x + bw / 2, 2, sub[i], fontName="Helvetica-Oblique", fontSize=7, fillColor=MUTED,
                         textAnchor="middle"))
        if i < n - 1:
            ax = x + bw + 2
            d.add(Line(ax, y0 + h / 2, ax + gap - 5, y0 + h / 2, strokeColor=ACC, strokeWidth=1.2))
            d.add(Polygon([ax + gap - 4, y0 + h / 2, ax + gap - 9, y0 + h / 2 + 3, ax + gap - 9, y0 + h / 2 - 3],
                          fillColor=ACC, strokeColor=ACC))
    return d


def footer(c, doc):
    c.saveState()
    c.setFont("Helvetica", 8)
    c.setFillColor(MUTED)
    c.drawString(20 * mm, 12 * mm, "On-Device AI with Flutter  |  Class Handbook")
    c.drawRightString(190 * mm, 12 * mm, f"Page {doc.page}")
    c.restoreState()


S = []

# ---------------- Cover ----------------
S += [Spacer(1, 55 * mm),
      p("On-Device AI with Flutter", ParagraphStyle("T", parent=H1, fontSize=30, leading=36)),
      p("Class handbook: build an app that identifies photos, understand how LLMs work, "
        "train your own model, and put a model on the internet.",
        ParagraphStyle("ST", parent=B, fontSize=13, leading=18, textColor=MUTED)),
      Spacer(1, 12 * mm),
      flow(["Take photo", "AI model\non the phone", "Answer\n\"golden retriever 91%\""]),
      Spacer(1, 18 * mm),
      p("<b>Contents</b>"),
      bullets(["1. The big picture: what AI, ML, neural networks and models are",
               "2. How LLMs (ChatGPT, Claude, Gemini) work",
               "3. Our Flutter app, step by step",
               "4. How to train your own model",
               "5. How to host a model on the internet",
               "6. Suggested lesson plan, exercises and glossary"]),
      PageBreak()]

# ---------------- 1. Big picture ----------------
S += [p("1. The Big Picture", H1),
      p("<b>Artificial Intelligence (AI)</b> is any program that does something we would call \"smart\". "
        "<b>Machine Learning (ML)</b> is the most common way to build AI today: instead of writing rules by hand, "
        "we show the computer thousands of examples and let it <i>learn</i> the rules itself."),
      p("A <b>model</b> is the result of that learning: a file full of numbers (called <b>weights</b> or "
        "<b>parameters</b>). Give the model an input (a photo, a sentence) and it does a lot of multiplication "
        "and addition with those weights to produce an output (a label, the next word)."),
      p("Normal programming vs. machine learning", H2),
      table([["", "Normal programming", "Machine learning"],
             ["You give", "Rules + data", "Data + correct answers (examples)"],
             ["You get", "Answers", "Rules (the model)"],
             ["Example", "if (pixel is orange && has whiskers) cat", "Show 10,000 labelled cat/dog photos; model learns the difference"]],
            [28, 66, 76]),
      p("Neural networks in one minute", H2),
      p("A neural network is layers of simple maths units (\"neurons\"). Each neuron takes numbers in, multiplies "
        "each by a weight, adds them up, and passes the result on. Stack many layers and the network can learn "
        "very complex patterns. For images, the early layers learn edges and colours, middle layers learn shapes "
        "(eyes, wheels), and the last layers learn whole objects (dog, car)."),
      flow(["Pixels", "Edges &\ncolours", "Shapes\n(eye, ear, wheel)", "Objects\n(dog, car)", "Scores for\neach label"],
           sub=["input", "early layers", "middle layers", "deep layers", "output"]),
      Spacer(1, 6),
      p("Training vs. inference", H2),
      bullets(["<b>Training</b> = learning. Slow, needs lots of data and usually a powerful GPU. Done once (or occasionally).",
               "<b>Inference</b> = using the trained model to make a prediction. Fast. This is what our app does on the phone, "
               "in a few milliseconds."]),
      p("On-device vs. cloud AI", H2),
      table([["", "On-device (our app)", "Cloud / API"],
             ["Internet needed", "No", "Yes"],
             ["Privacy", "Photo never leaves the phone", "Photo is uploaded to a server"],
             ["Speed", "Very fast (no network trip)", "Depends on network"],
             ["Model size", "Small (MBs) - limited power", "Huge models possible (GBs+)"],
             ["Cost", "Free per use", "You pay for servers / per request"],
             ["Updating the model", "Ship app update or download new file", "Swap it on the server instantly"]],
            [36, 67, 67]),
      CondPageBreak(90 * mm)]

# ---------------- 2. LLMs ----------------
S += [p("2. How Large Language Models (LLMs) Work", H1),
      p("An LLM such as ChatGPT, Claude or Gemini is a neural network trained to do one thing extremely well: "
        "<b>predict the next piece of text</b>. Everything else - answering questions, writing code, translating - "
        "emerges from doing that one task at enormous scale."),
      tip("Important for the class", "Our photo app uses an <b>image classifier</b> (a CNN called EfficientNet-Lite), not an LLM. "
          "Both are neural networks and follow the same train -> convert -> run pattern, but they are built for different "
          "jobs. Modern \"multimodal\" LLMs combine both: they can read images and text together."),
      p("Step 1 - Tokens: turning text into numbers", H2),
      p("Computers only understand numbers, so text is chopped into <b>tokens</b> (whole words or pieces of words) "
        "and each token gets an ID number. Roughly, 1 token is about 3/4 of an English word."),
      code('"Flutter is awesome"  ->  ["Fl", "utter", " is", " awesome"]  ->  [3061, 6339, 374, 12738]'),
      p("Step 2 - Embeddings: numbers with meaning", H2),
      p("Each token ID is turned into a long list of numbers (a <b>vector</b>, often thousands of numbers long) called an "
        "<b>embedding</b>. Words with similar meaning end up with similar vectors, so \"king\" is close to \"queen\" and "
        "\"dog\" is close to \"puppy\". The model learns these during training."),
      p("Step 3 - The Transformer and attention", H2),
      p("The core of every modern LLM is the <b>Transformer</b> (introduced by Google in 2017 in the paper "
        "<i>\"Attention Is All You Need\"</i>). Its key trick is <b>attention</b>: for every word, the model looks at all "
        "the other words and decides which ones matter for understanding it."),
      code('"The animal didn\'t cross the street because IT was too tired."\n'
           '   Attention lets the model work out that "IT" refers to "animal", not "street".'),
      p("A Transformer stacks dozens of these attention layers. Each layer refines the understanding a bit more."),
      p("Step 4 - Predict the next token, repeat", H2),
      flow(["Your prompt\n\"The sky is\"", "Tokenise", "Transformer\nlayers", "Probabilities\nblue 62%, clear 9%...",
            "Pick one\n-> \"blue\""]),
      Spacer(1, 4),
      p("The model outputs a probability for every token in its vocabulary. One is picked (the <b>temperature</b> setting "
        "controls how adventurous the pick is), added to the text, and the whole thing runs again to get the next token. "
        "That is why answers appear word by word."),
      CondPageBreak(90 * mm),
      p("How an LLM is trained", H2),
      table([["Stage", "What happens", "Data"],
             ["1. Pre-training", "Model reads a huge amount of text and learns to predict the next token. It learns grammar, "
              "facts and reasoning patterns. Costs millions of dollars of GPU time.", "Trillions of tokens: web pages, books, code"],
             ["2. Fine-tuning (instruction tuning)", "Model is trained further on examples of good question/answer conversations "
              "so it behaves like a helpful assistant instead of just continuing text.", "Thousands to millions of curated example chats"],
             ["3. Preference tuning (RLHF / RLAIF)", "Humans (or AI feedback guided by principles) compare answers and pick the "
              "better one. The model is nudged towards the preferred style: helpful, honest, safe.", "Rankings of answers"]],
            [40, 88, 42]),
      p("How the model actually learns (for any neural network)", H2),
      bullets(["Start with random weights - the model is useless.",
               "Show it an example and let it guess (e.g. next word, or \"cat\").",
               "Measure how wrong the guess was. This number is the <b>loss</b>.",
               "Use <b>backpropagation</b> + <b>gradient descent</b> to nudge every weight slightly in the direction that "
               "would have made the loss smaller.",
               "Repeat millions or billions of times. The weights slowly become good."]),
      p("Key words to know", H2),
      table([["Term", "Meaning"],
             ["Parameters", "The learned numbers in the model. Small LLMs have ~1 billion, frontier models far more."],
             ["Context window", "How many tokens the model can \"see\" at once (your prompt + its answer)."],
             ["Hallucination", "When a model confidently states something false. It predicts plausible text, not verified truth."],
             ["Quantization", "Storing weights with fewer bits (e.g. 8-bit instead of 32-bit) so the model is smaller and faster. "
              "Our app's models are quantized: EfficientNet-Lite4 is 15 MB instead of about 50 MB."],
             ["RAG", "Retrieval-Augmented Generation: look up relevant documents first, paste them into the prompt, then answer."],
             ["Fine-tuning / LoRA", "Further training on your own data. LoRA trains a small add-on instead of the whole model, "
              "so it is much cheaper."]],
            [36, 134]),
      tip("Can an LLM run on a phone?", "Yes - small models (around 1-4 billion parameters, quantized) can. For Flutter, look at "
          "packages built on Google's MediaPipe LLM Inference (e.g. <font face='Courier'>flutter_gemma</font>) or Apple's "
          "on-device Foundation Models on iOS. They follow exactly the same idea as our app: ship a model file, load it, run it locally."),
      CondPageBreak(90 * mm)]

# ---------------- 3. App ----------------
S += [p("3. Our Flutter App, Step by Step", H1),
      p("The app lets you take (or pick) a photo and tells you what is in it, with a confidence percentage. "
        "Everything runs on the phone using <b>TensorFlow Lite</b> (now also branded <b>LiteRT</b>) through the "
        "<font face='Courier'>tflite_flutter</font> package. No internet, no API key."),
      p("Features", H2),
      table([["Feature", "How to use it"],
             ["Camera / Gallery", "Buttons at the bottom. The buttons lock while the camera is open, so a double tap cannot crash it."],
             ["Model switch", "Chip icon in the top bar: EfficientNet-Lite4 (accurate) or MobileNet V1 (fast). Great for comparing in class."],
             ["Retry", "Button under the results: runs the same photo again with the currently selected model."],
             ["History", "Clock icon. Every result is saved on the phone (photo, answer, model, speed) and survives restarts. "
              "Tap to reopen, swipe left to delete, bin icon to clear all."],
             ["Clear", "X icon in the top bar resets the screen."],
             ["\"Not very sure\" hint", "Shown when the top answer is below 30% confidence."]], [38, 132]),
      p("The two models", H2),
      table([["", "EfficientNet-Lite4 (default)", "MobileNet V1"],
             ["Accuracy (ImageNet top-1)", "81.5%", "about 70%"],
             ["File size", "15 MB", "4 MB"],
             ["Input", "[1, 300, 300, 3] uint8 (0-255)", "[1, 224, 224, 3] uint8 (0-255)"],
             ["Output", "[1, 1000] uint8 (quantized scores)", "[1, 1001] uint8 (\"background\" + 1000)"],
             ["Best for", "Accuracy", "Speed, small app size"]], [44, 63, 63]),
      p("Both were made by Google and trained on <b>ImageNet</b> (about 1.2 million photos, 1000 categories: animals, food, "
        "vehicles, everyday objects). On test photos the difference is clear:"),
      table([["Photo", "MobileNet V1", "EfficientNet-Lite4"],
             ["Labrador", "Eskimo dog 31% (wrong)", "Labrador retriever 66%"],
             ["Cat in snow", "lynx 49% (wrong)", "Egyptian cat 56%"],
             ["Daisy", "daisy 75%", "daisy 91%"]], [44, 63, 63]),
      tip("Limitation to discuss in class", "Both models only know the same 1000 ImageNet categories. Show them a person or a phone "
          "screenshot and they will still pick the closest of those 1000 - often wrongly. A bigger model is more accurate, "
          "but it cannot know things it was never taught. Fixing that is what section 4 (training your own model) is for."),
      p("Project structure", H2),
      code("""ondevice_ai/
  assets/models/
    efficientnet_lite4.tflite  <- accurate model (the "brain" file)
    labels_1000.txt            <- 1000 names, same order as the model output
    mobilenet.tflite           <- small, fast model
    mobilenet_labels.txt       <- 1001 names ("background" first)
  lib/
    main.dart                  <- starts the app
    models/model_config.dart   <- list of models the app can use
    models/prediction.dart     <- a label + confidence
    models/history_entry.dart  <- one saved result
    services/classifier.dart   <- ALL the AI code (4 steps)
    services/history_store.dart<- saves history to the phone
    screens/home_screen.dart   <- camera, results, Retry, Clear, model switch
    screens/history_screen.dart<- list of past results
  pubspec.yaml                 <- packages + registers the model files as assets"""),
      p("Packages used", H2),
      table([["Package", "Why"],
             ["tflite_flutter", "Loads the .tflite model and runs it on the device"],
             ["image_picker", "Opens the camera or photo gallery"],
             ["image", "Decodes the photo, crops and resizes it to the model's size"],
             ["path_provider", "Finds the app's private folder where history is saved"]], [40, 130]),
      p("The 4 steps of on-device AI (lib/services/classifier.dart)", H2),
      flow(["1. LOAD\nmodel + labels", "2. PREPROCESS\ncrop + resize to\nmodel's size", "3. RUN\ninterpreter.invoke()",
            "4. POSTPROCESS\nde-quantize, sort,\ntop 3"]),
      Spacer(1, 6),
      p("The classifier asks the model what it expects instead of hard-coding it. That is why the same code works for "
        "EfficientNet, MobileNet, or a model you train yourself."),
      p("<b>Step 1 - Load.</b> Done once when the app starts (and again when you switch model)."),
      code("""_interpreter = await Interpreter.fromAsset(config.modelPath);
final labelsText = await rootBundle.loadString(config.labelsPath);
_labels = labelsText.split('\\n')
    .map((l) => l.trim()).where((l) => l.isNotEmpty)
    .map((l) => l.replaceFirst(RegExp(r'^\\d+\\s+'), ''))   // "0 Apple" -> "Apple"
    .toList();

// Ask the model what it wants. Shape is [1, height, width, 3].
final input = _interpreter.getInputTensor(0);
_inputSize = input.shape[1];          // 300 for EfficientNet, 224 for MobileNet
print('input: ${input.shape} ${input.type} ${input.params}');"""),
      p("<b>Step 2 - Preprocess.</b> Each model was trained on square images of one exact size, so every photo must be converted "
        "to that: decode, centre-crop to a square (so the object is not squashed), resize, then take the R, G, B bytes. "
        "This is slow for big photos, so it runs on a background isolate to keep the UI smooth."),
      code("""final decoded = img.bakeOrientation(img.decodeImage(bytes)!);   // fix camera rotation
final side = min(decoded.width, decoded.height);
final cropped = img.copyCrop(decoded,
    x: (decoded.width - side) ~/ 2, y: (decoded.height - side) ~/ 2,
    width: side, height: side);
final resized = img.copyResize(cropped, width: size, height: size,
    interpolation: img.Interpolation.average);
return resized.getBytes(order: img.ChannelOrder.rgb);   // size*size*3 bytes, 0..255

// Called through:  Isolate.run(() => _preprocess(bytes, size))"""),
      p("<b>Step 3 - Run.</b> Copy the pixels into the model's input, call <font face='Courier'>invoke()</font>, read the output."),
      code("""final input = _interpreter.getInputTensor(0);
final output = _interpreter.getOutputTensor(0);
if (input.type == TensorType.uint8) {
  input.data = rgb;                         // quantized model: raw 0..255 bytes
} else {
  input.data = Float32List.fromList(        // float model: 0.0..255.0
      rgb.map((v) => v.toDouble()).toList()).buffer.asUint8List();
}
_interpreter.invoke();                      // <- the actual AI happens here"""),
      p("<b>Step 4 - Postprocess.</b> A quantized model answers in bytes (0-255). Convert them back to real numbers with the "
        "scale and zero point stored in the model, then pick the top 3."),
      code("""final raw = Uint8List.fromList(output.data);
final scores = output.type == TensorType.uint8
    ? [for (final b in raw) (b - q.zeroPoint) * q.scale]   // q = output.params
    : raw.buffer.asFloat32List().toList();

final predictions = [
  for (var i = 0; i < scores.length; i++) Prediction(_labels[i], scores[i]),
]..sort((a, b) => b.confidence.compareTo(a.confidence));
return predictions.take(3).toList();"""),
      tip("Golden rule", "Preprocessing in the app must match what was done during training: same image size, same colour "
          "order, same number range. Most \"my model gives garbage\" bugs are a preprocessing mismatch. We checked this "
          "for EfficientNet-Lite4 by testing raw vs. normalized pixels on known photos - raw 0-255 bytes scored better."),
      p("History and Retry", H2),
      p("After each run, <font face='Courier'>HistoryStore</font> copies the photo into the app's private Documents folder and "
        "adds an entry to <font face='Courier'>history/history.json</font>. Only the file name is stored, not the full path, "
        "because iOS changes the app's folder path on every reinstall. <b>Retry</b> simply calls the same "
        "<font face='Courier'>classify()</font> again on the saved photo, with whichever model is selected - an easy way to "
        "compare models on the same image."),
      p("Running the app", H2),
      code("""flutter pub get
flutter run                 # debug: hot reload, slower AI
flutter run --release       # release: full speed - use this to measure timings
# Android: minSdk is set to 26 in android/app/build.gradle.kts
# iOS: camera + photo permissions are already in ios/Runner/Info.plist
#      (iOS simulator has no camera - use the Gallery button)"""),
      CondPageBreak(90 * mm)]

# ---------------- 4. Training ----------------
S += [p("4. How to Train Your Own Model", H1),
      p("Say the class wants an app that recognises <b>three kinds of plants</b>, or <b>apples vs. bananas vs. oranges</b>. "
        "Our ImageNet models do not know these exactly, so we train our own model. The good news: we do not start from zero."),
      p("Transfer learning - the shortcut", H2),
      p("Training a model from scratch needs millions of images. <b>Transfer learning</b> re-uses a model that already "
        "learned to \"see\" (edges, shapes, textures) and only trains the final layer to recognise our new categories. "
        "You can get good results with <b>50-200 photos per category</b> in a few minutes on a laptop or free Google Colab."),
      flow(["MobileNet\n(already knows\nedges & shapes)", "FREEZE these\nlayers", "NEW last layer\n(your classes)",
            "Train on\nyour photos", "model.tflite\n+ labels.txt"]),
      Spacer(1, 6),
      p("Option A - No code: Google Teachable Machine", H2),
      bullets(["Go to <b>teachablemachine.withgoogle.com</b> -> Image Project -> Standard image model.",
               "Create one class per category and add photos (upload or webcam).",
               "Click <b>Train Model</b>, test it in the browser.",
               "Export -> TensorFlow Lite -> Quantized. You get <font face='Courier'>model.tflite</font> and "
               "<font face='Courier'>labels.txt</font>.",
               "Perfect for a live classroom demo: train in 5 minutes, drop into the app."]),
      tip("Teachable Machine tips", "Choose the <b>Quantized</b> TensorFlow Lite export. Its labels.txt lines look like "
          "<font face='Courier'>0 Apple</font> - the app strips the number automatically."),
      p("Option B - Python + TensorFlow (Google Colab, free GPU)", H2),
      p("1. Collect images into one folder per category:"),
      code("""dataset/
  apple/   img001.jpg img002.jpg ...
  banana/  ...
  orange/  ..."""),
      p("2. Train with transfer learning and export to TensorFlow Lite:"),
      code("""import tensorflow as tf

IMG = (224, 224)
train_ds = tf.keras.utils.image_dataset_from_directory(
    "dataset", validation_split=0.2, subset="training", seed=42, image_size=IMG)
val_ds = tf.keras.utils.image_dataset_from_directory(
    "dataset", validation_split=0.2, subset="validation", seed=42, image_size=IMG)
class_names = train_ds.class_names

# A pretrained "eye" - we keep its knowledge frozen
base = tf.keras.applications.MobileNetV2(input_shape=IMG + (3,),
                                         include_top=False, weights="imagenet")
base.trainable = False

model = tf.keras.Sequential([
    tf.keras.layers.RandomFlip("horizontal"),        # data augmentation
    tf.keras.layers.RandomRotation(0.1),
    tf.keras.layers.Rescaling(1/127.5, offset=-1),   # 0..255 -> -1..1
    base,
    tf.keras.layers.GlobalAveragePooling2D(),
    tf.keras.layers.Dropout(0.2),
    tf.keras.layers.Dense(len(class_names), activation="softmax"),  # our new layer
])
model.compile(optimizer="adam", loss="sparse_categorical_crossentropy", metrics=["accuracy"])
model.fit(train_ds, validation_data=val_ds, epochs=10)

# Convert for mobile
converter = tf.lite.TFLiteConverter.from_keras_model(model)
converter.optimizations = [tf.lite.Optimize.DEFAULT]   # makes it ~4x smaller
open("model.tflite", "wb").write(converter.convert())
open("labels.txt", "w").write("\\n".join(class_names))"""),
      p("3. Put it in the app", H2),
      p("No changes to the AI code are needed - the classifier reads the input size and type from the model. Three steps:"),
      bullets(["Copy <font face='Courier'>model.tflite</font> and <font face='Courier'>labels.txt</font> into "
               "<font face='Courier'>assets/models/</font> (e.g. as <font face='Courier'>fruit.tflite</font> and "
               "<font face='Courier'>fruit_labels.txt</font>).",
               "List both files under <font face='Courier'>assets:</font> in pubspec.yaml.",
               "Add a <font face='Courier'>ModelConfig</font> in lib/models/model_config.dart and put it in "
               "<font face='Courier'>all</font>. It appears in the model switch menu."]),
      code("""static const fruit = ModelConfig(
  name: 'Fruit (ours)',
  description: 'Trained in class · 3 classes',
  modelPath: 'assets/models/fruit.tflite',
  labelsPath: 'assets/models/fruit_labels.txt',
);

static const all = [efficientNet, mobileNet, fruit];"""),
      p("The Keras model above takes <b>float</b> input 0-255 (the Rescaling layer is inside the model) and gives float "
        "probabilities, which the app's float path handles. A Teachable Machine <b>Quantized</b> export takes uint8 input, "
        "which the app also handles. Its <font face='Courier'>0 Apple</font>-style labels are cleaned up automatically."),
      tip("Teaching moment", "Print <font face='Courier'>_interpreter.getInputTensor(0)</font> and "
          "<font face='Courier'>getOutputTensor(0)</font> - the shape and type (uint8 vs float32) tell you exactly how to "
          "pre- and post-process. Our app already prints these on startup."),
      p("Tips for good results", H2),
      bullets(["Variety beats quantity: different lighting, angles, backgrounds, distances.",
               "Keep categories balanced (similar number of photos each).",
               "Hold back 20% of photos for validation - if training accuracy is high but validation is low, the model is "
               "<b>overfitting</b> (memorising instead of learning). Add more varied data or augmentation.",
               "Add an \"other / nothing\" class so the model has somewhere to put unknown things."]),
      p("What about training an LLM?", H2),
      p("Training an LLM from scratch is not practical for a class (it needs huge GPU clusters). What people actually do is "
        "<b>fine-tune</b> an existing open model (e.g. Llama, Gemma, Mistral, Qwen) on their own examples using <b>LoRA</b>, "
        "with tools such as Hugging Face <font face='Courier'>transformers</font> + <font face='Courier'>peft</font>, or "
        "Unsloth on a free Colab GPU. The workflow is identical in spirit: prepare example data -> train -> evaluate -> export. "
        "Often, good prompting or RAG is enough and no training is needed at all."),
      CondPageBreak(90 * mm)]

# ---------------- 5. Hosting ----------------
S += [p("5. How to Host a Model on the Internet", H1),
      p("There are two different things people mean by \"hosting a model\". Pick based on where you want the AI to run."),
      table([["Approach", "Where AI runs", "Good for"],
             ["A. Host the model FILE online, app downloads it", "On the phone", "Updating the model without an app-store release; keeping the app small"],
             ["B. Host the model as an API (web service)", "On a server", "Big models, web apps, one model shared by Android/iOS/web"],
             ["C. Host an LLM", "On a GPU server", "Chatbots, text generation"]], [62, 36, 72]),
      p("A. Host the .tflite file and download it at runtime", H2),
      p("Upload <font face='Courier'>model.tflite</font> to any file host: <b>Firebase ML custom models</b> (built for this, "
        "handles versioning), Firebase Storage, GitHub Releases, or any CDN. The app downloads it once, saves it, and loads "
        "it from a file instead of from assets:"),
      code("""// pubspec: http, path_provider
final dir = await getApplicationDocumentsDirectory();
final file = File('${dir.path}/model.tflite');
if (!await file.exists()) {
  final res = await http.get(Uri.parse('https://YOUR-HOST/model.tflite'));
  await file.writeAsBytes(res.bodyBytes);
}
_interpreter = Interpreter.fromFile(file);   // instead of fromAsset"""),
      p("B. Host the model as a web API (Python FastAPI)", H2),
      p("The phone uploads the photo, the server runs the model, and sends back JSON. Create three files:"),
      p("<b>main.py</b>"),
      code("""import io
import numpy as np
from fastapi import FastAPI, UploadFile
from PIL import Image
from ai_edge_litert.interpreter import Interpreter   # pip install ai-edge-litert
                                                     # (or tf.lite.Interpreter)
app = FastAPI()
interp = Interpreter(model_path="model.tflite")
interp.allocate_tensors()
inp, out = interp.get_input_details()[0], interp.get_output_details()[0]
labels = open("labels.txt").read().splitlines()

@app.post("/predict")
async def predict(file: UploadFile):
    img = Image.open(io.BytesIO(await file.read())).convert("RGB").resize((224, 224))
    x = np.expand_dims(np.asarray(img, dtype=inp["dtype"]), 0)   # [1,224,224,3]
    interp.set_tensor(inp["index"], x)
    interp.invoke()
    scores = interp.get_tensor(out["index"])[0].astype(float)
    if out["dtype"] == np.uint8:
        scores /= 255.0                                          # quantized model
    top = scores.argsort()[::-1][:3]
    return [{"label": labels[i], "confidence": float(scores[i])} for i in top]"""),
      p("<b>requirements.txt</b> and <b>Dockerfile</b>"),
      code("""# requirements.txt
fastapi
uvicorn[standard]
python-multipart
pillow
numpy
ai-edge-litert

# Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}"]"""),
      p("Test locally with <font face='Courier'>uvicorn main:app --reload</font>, then open "
        "<font face='Courier'>http://localhost:8000/docs</font> - FastAPI gives you a free test page to upload an image."),
      p("Where to deploy it", H2),
      table([["Platform", "How", "Notes"],
             ["Google Cloud Run", "<font face='Courier'>gcloud run deploy --source . --allow-unauthenticated</font>",
              "Builds the Dockerfile, gives an https URL, scales to zero (free tier covers a class)"],
             ["Hugging Face Spaces", "Create a Space -> Docker SDK -> push these files",
              "Free CPU hosting, great for demos and sharing"],
             ["Render / Railway / Fly.io", "Connect GitHub repo, it detects the Dockerfile", "Simple, free/cheap tiers"],
             ["AWS / Azure", "App Runner, Lambda (container), Azure Container Apps", "More setup; common in companies"]],
            [36, 72, 62]),
      p("Calling the API from Flutter", H2),
      code("""// pubspec: http
final req = http.MultipartRequest('POST', Uri.parse('https://YOUR-URL/predict'))
  ..files.add(await http.MultipartFile.fromPath('file', imageFile.path));
final res = await http.Response.fromStream(await req.send());
final List results = jsonDecode(res.body);   // [{label, confidence}, ...]"""),
      p("C. Hosting an LLM", H2),
      bullets(["<b>Easiest - use a provider API</b>: Anthropic (Claude), OpenAI, Google (Gemini). No servers, pay per token. "
               "Never put the API key inside the Flutter app - call it from your own small backend.",
               "<b>Run an open model yourself</b>: <font face='Courier'>ollama run llama3.2</font> on a laptop gives you a "
               "local LLM with an HTTP API on port 11434 - great for class.",
               "<b>Production self-hosting</b>: rent a GPU server and run <b>vLLM</b> "
               "(<font face='Courier'>vllm serve &lt;model-name&gt;</font>), which exposes an OpenAI-compatible API. "
               "Or use managed options: Hugging Face Inference Endpoints, Google Vertex AI, AWS Bedrock/SageMaker.",
               "Remember: LLMs need GPUs with lots of memory. A 7-8 billion parameter model needs roughly 16 GB of GPU "
               "memory at 16-bit, or about 5-6 GB when 4-bit quantized."]),
      p("Security checklist for any hosted model", H2),
      bullets(["Use HTTPS only. Never ship secret API keys inside a mobile app.",
               "Limit upload size and add rate limiting so nobody can run up your bill.",
               "Add authentication (e.g. Firebase Auth token) before exposing it publicly.",
               "Be clear with users that their photos are uploaded (privacy) - or keep it on-device!"]),
      CondPageBreak(90 * mm)]

# ---------------- 6. Lesson plan ----------------
S += [p("6. Suggested Lesson Plan", H1),
      table([["Session", "Topic", "Activity"],
             ["1 (60 min)", "What is AI / ML / a model; on-device vs cloud", "Demo the finished app; students guess what it will get wrong"],
             ["2 (90 min)", "Build the app: assets, packages, the 4 steps", "Live-code classifier.dart step by step; print tensor shapes; switch model and Retry the same photo"],
             ["3 (60 min)", "How LLMs work: tokens, attention, next-token prediction", "Use an online tokenizer to see how text becomes tokens"],
             ["4 (90 min)", "Train your own model", "Teachable Machine in groups, swap the model into the app"],
             ["5 (90 min)", "Host a model", "Run the FastAPI server locally, call it from Flutter, deploy to Cloud Run or HF Spaces"]],
            [24, 70, 76]),
      p("Exercises", H2),
      bullets(["<b>Easy:</b> Show the top 5 results instead of 3. Hide results below 10% confidence.",
               "<b>Easy:</b> Change the \"Not very sure\" threshold from 30% and see how often it appears.",
               "<b>Easy:</b> Remember the selected model between app launches (e.g. with shared_preferences).",
               "<b>Medium:</b> Add a \"Compare\" button that runs both models on the same photo and shows them side by side.",
               "<b>Medium:</b> Search or filter the History screen by label.",
               "<b>Medium:</b> Live camera mode with the <font face='Courier'>camera</font> package: classify a frame every 500 ms.",
               "<b>Medium:</b> Train a Teachable Machine model for 3 classroom objects and swap it in.",
               "<b>Hard:</b> Add a toggle: \"On-device\" vs \"Cloud\" - call your hosted FastAPI and compare speed.",
               "<b>Hard:</b> Download the model at runtime (section 5A) and update it without rebuilding the app."]),
      p("Troubleshooting", H2),
      table([["Problem", "Fix"],
             ["Unable to load asset", "Check pubspec.yaml assets paths and indentation, then run flutter pub get and a full restart (not hot reload)."],
             ["Input/output shape or type error", "Print getInputTensor(0) / getOutputTensor(0). Match the shape, and use int for uint8 models, double for float32 models."],
             ["Predictions are nonsense", "Preprocessing mismatch: wrong size, wrong value range, or labels.txt in the wrong order / extra lines."],
             ["Android: Inconsistent JVM-target compatibility (tflite_flutter)", "Already fixed in android/build.gradle.kts: the plugin's Kotlin jvmTarget is set to 11."],
             ["PlatformException(multiple_request)", "Camera opened twice by a double tap. The app now locks the buttons while the picker is open."],
             ["iOS: flutter install fails with no clear reason", "Use flutter run --release, or install the built app with: xcrun devicectl device install app --device DEVICE_ID build/ios/iphoneos/Runner.app"],
             ["Android build fails on minSdk", "Set minSdk to 26 in android/app/build.gradle.kts."],
             ["iOS crashes when opening camera", "Missing NSCameraUsageDescription in Info.plist. The simulator has no camera - use Gallery."],
             ["iOS build errors about TensorFlowLiteC", "cd ios && pod install --repo-update, then rebuild."]],
            [52, 118]),
      p("Glossary", H2),
      table([["Term", "Meaning"],
             ["Tensor", "A multi-dimensional array of numbers. [1, 224, 224, 3] = 1 image, 224 rows, 224 columns, 3 colours."],
             ["CNN", "Convolutional Neural Network - the standard network type for images. MobileNet and EfficientNet-Lite are small, fast CNNs for phones."],
             ["Inference", "Running a trained model to get a prediction."],
             ["Epoch", "One full pass over the training data."],
             ["Loss", "A number measuring how wrong the model is. Training tries to make it smaller."],
             ["Overfitting", "Model memorises training data and fails on new data."],
             ["TFLite / LiteRT", "Google's format and runtime for running models on phones and small devices."],
             ["Zero point / scale", "How a quantized model stores real numbers as bytes: real = (byte - zero point) x scale."],
             ["Isolate", "Dart's version of a background thread. Used so image preparation does not freeze the UI."],
             ["Transfer learning", "Re-using a pretrained model and training only the last part on your own data."]],
            [36, 134]),
      Spacer(1, 8),
      p("Further reading: \"Attention Is All You Need\" (Vaswani et al., 2017); Google AI Edge / LiteRT documentation; "
        "the tflite_flutter package page on pub.dev; Jay Alammar's \"The Illustrated Transformer\"; "
        "Andrej Karpathy's \"Intro to Large Language Models\" talk.", SM)]

doc = SimpleDocTemplate(OUT, pagesize=A4, leftMargin=20 * mm, rightMargin=20 * mm, topMargin=18 * mm,
                        bottomMargin=20 * mm, title="On-Device AI with Flutter - Class Handbook",
                        author="Training", subject="Flutter on-device AI, LLMs, training and hosting")
doc.build(S, onFirstPage=lambda c, d: None, onLaterPages=footer)
print("ok", OUT)
