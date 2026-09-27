// OCR über Apple Vision für einen Ordner voller Frames (JPG/PNG).
// Aufruf: ocr_vision <ordner> <fps> > ocr.jsonl
// Ausgabe je Frame eine JSON-Zeile: {"datei":…, "t":Sekunde, "texte":[{"text":…, "conf":…, "x":…, "y":…, "w":…, "h":…}]}
// Boxen in Anteilen des Bildes (0–1), y von OBEN gemessen (Vision misst von unten — hier umgerechnet).
import Foundation
import Vision
import AppKit

let args = CommandLine.arguments
guard args.count >= 3, let fps = Double(args[2]) else {
    FileHandle.standardError.write("Aufruf: ocr_vision <ordner> <fps>\n".data(using: .utf8)!)
    exit(2)
}
let ordner = URL(fileURLWithPath: args[1])
let dateien = (try? FileManager.default.contentsOfDirectory(at: ordner, includingPropertiesForKeys: nil))?
    .filter { ["jpg", "jpeg", "png"].contains($0.pathExtension.lowercased()) }
    .sorted { $0.lastPathComponent < $1.lastPathComponent } ?? []

for (i, datei) in dateien.enumerated() {
    guard let bild = NSImage(contentsOf: datei),
          let cg = bild.cgImage(forProposedRect: nil, context: nil, hints: nil) else { continue }
    let anfrage = VNRecognizeTextRequest()
    anfrage.recognitionLevel = .accurate
    anfrage.usesLanguageCorrection = false
    anfrage.recognitionLanguages = ["en-US"]
    let handler = VNImageRequestHandler(cgImage: cg, options: [:])
    try? handler.perform([anfrage])
    var texte: [[String: Any]] = []
    for beob in (anfrage.results ?? []) {
        guard let kand = beob.topCandidates(1).first else { continue }
        let b = beob.boundingBox
        texte.append(["text": kand.string, "conf": Double(kand.confidence),
                      "x": Double(b.minX), "y": Double(1 - b.maxY), "w": Double(b.width), "h": Double(b.height)])
    }
    let zeile: [String: Any] = ["datei": datei.lastPathComponent, "t": Double(i) / fps, "texte": texte]
    if let daten = try? JSONSerialization.data(withJSONObject: zeile), let s = String(data: daten, encoding: .utf8) {
        print(s)
    }
}
