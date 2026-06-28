from openrag import RAG


def main() -> None:
    rag = RAG()
    rag.add("docs/policy.txt")

    answer = rag.ask("What is the leave policy?")
    print(answer)


if __name__ == "__main__":
    main()
