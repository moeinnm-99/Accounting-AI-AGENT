from agent import build_graph
import json

def test_agent():
    with open("sample_data.json", "r") as f:
        data = json.load(f)

    graph = build_graph()
    result = graph.invoke(data)

    assert "profit" in result
    assert "recommendations" in result
    assert isinstance(result["recommendations"], list)

    with open("output.json", "w") as f:
        json.dump(result, f, indent=4)

    print("✅ Test passed.")
    print("📁 Output saved to output.json")
    print(result)


if __name__ == "__main__":
    test_agent()
