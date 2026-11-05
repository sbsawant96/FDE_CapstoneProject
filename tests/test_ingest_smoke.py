import json
import os
from src.ingest.normalizer import normalize_ticket

def test_four_channel_normalization():
    data_path = os.path.join(os.path.dirname(__file__), "..", "data", "development_tickets.json")
    assert os.path.exists(data_path), f"Missing data file at {data_path}"
    
    with open(data_path, "r", encoding="utf-8") as f:
        tickets = json.load(f)

    channels_found = set()
    normalized_samples = {}

    for t in tickets:
        norm = normalize_ticket(t)
        assert norm.ticket_id != "UNKNOWN"
        assert len(norm.processed_text) > 0
        channels_found.add(norm.channel)
        if norm.channel not in normalized_samples:
            normalized_samples[norm.channel] = norm

    expected_channels = {"email", "chat", "docs_comment", "forum"}
    missing = expected_channels - channels_found
    assert not missing, f"Missing channel types in dataset: {missing}"

    print(f"Successfully normalized {len(tickets)} tickets across all 4 channels: {sorted(list(channels_found))}")
    for ch, sample in normalized_samples.items():
        print(f"[{ch.upper()}] {sample.ticket_id} -> Length: {len(sample.processed_text)} chars")

if __name__ == "__main__":
    test_four_channel_normalization()
