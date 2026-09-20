from app.services.llm_gateway import llm_gateway


def main():
    response = llm_gateway.invoke(
        """
        You are a marketing intelligence assistant.

        Explain in 3 short points why AI is becoming
        important in modern marketing.
        """
    )

    print("\n===== GPT-OSS 20B RESPONSE =====\n")
    print(response.content)


if __name__ == "__main__":
    main()