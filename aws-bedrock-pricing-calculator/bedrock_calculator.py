import streamlit as st
import tiktoken
import requests
import urllib.parse

def load_pricing():
    url = "https://raw.githubusercontent.com/pjawale-cohere/ml-demos/main/aws-bedrock-pricing-calculator/pricing_data_on_demand_batch.json"
    response = requests.get(url)
    return response.json()

def format_currency(value):
    return "${:,.4f}".format(value)

def count_tokens(text, encoding_name='cl100k_base'):
    encoding = tiktoken.get_encoding(encoding_name)
    return len(encoding.encode(text))

def main():
    st.set_page_config(page_title="AWS Bedrock Pricing Calculator", page_icon=":money_with_wings:")

    # Custom CSS styles
    st.markdown("""
    <style>
        .container {
            display: flex;
        }
        .left-column {
            flex: 1;
            padding-right: 20px;
        }
        .right-column {
            width: 300px;
        }
    </style>
    """, unsafe_allow_html=True)

    # Main content
    with st.container():
        st.title("AWS Bedrock Pricing Calculator")

        # Pricing Calculator
        st.subheader("Pricing Calculator")
        pricing_data = load_pricing()

        # Read URL parameters
        params = st.experimental_get_query_params()
        model_type = params.get("model_type", [list(pricing_data.keys())[0]])[0]
        input_tokens = int(params.get("input_tokens", [0])[0])
        output_tokens = int(params.get("output_tokens", [0])[0])
        number_of_calls = int(params.get("number_of_calls", [0])[0])

        model_type = st.selectbox("Select Model Type", list(pricing_data.keys()), index=list(pricing_data.keys()).index(model_type), help="Choose the model type for pricing calculation.")

        # Display pricing information
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Input Token Price per 1,000", pricing_data[model_type]["Price per 1,000 input tokens"])
        with col2:
            st.metric("Output Token Price per 1,000", pricing_data[model_type]["Price per 1,000 output tokens"])

        input_tokens = st.number_input("Number of Input Tokens (per example)", min_value=0, step=1, value=input_tokens, help="Provide the number of input tokens.", format="%d")
        output_tokens = st.number_input("Number of Output Tokens (per example)", min_value=0, step=1, value=output_tokens, help="Provide the number of output tokens.", format="%d")
        number_of_calls = st.number_input("Estimated Monthly Calls (Optional)", min_value=0, step=1, value=number_of_calls, help="Provide the estimated monthly call volume.", format="%d")

        if st.button("Calculate Cost") or params:
            input_price = float(pricing_data[model_type]["Price per 1,000 input tokens"].strip('$'))
            output_price = float(pricing_data[model_type]["Price per 1,000 output tokens"].strip('$'))

            input_cost = input_price * (input_tokens / 1000)
            output_cost = output_price * (output_tokens / 1000)
            # total_cost = input_cost + output_cost
            monthly_cost = total_cost * number_of_calls if number_of_calls > 0 else 0

            # Display the cost breakdown
            st.success(f"Input Cost: {format_currency(input_cost)}")
            st.success(f"Output Cost: {format_currency(output_cost)}")
            # st.success(f"Total Cost: {format_currency(total_cost)}")
            if monthly_cost:
                st.success(f"Monthly Cost: {format_currency(monthly_cost)}")

            # Add a "Share" button
            params = {
                "model_type": model_type,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "number_of_calls": number_of_calls
            }
            share_url = f"https://bedrock-budgeter.streamlit.app/?{urllib.parse.urlencode(params)}"
            st.markdown(f"<a href='{share_url}' target='_blank'>Share Results</a>", unsafe_allow_html=True)

        # Reset button
        if st.button("Reset"):
            st.experimental_set_query_params()
            st.experimental_rerun()

        # Token Estimator
        st.subheader("Token Estimator")
        user_text = st.text_area("Enter your text:", height=150, help="Paste your text here to estimate the token count.")

        if st.button("Estimate Tokens"):
            token_count = count_tokens(user_text)
            st.info(f"Estimated Token Count: {token_count}")

    # About section (sidebar)
    with st.sidebar:
        st.header("About")
        st.markdown("""
        This app helps you estimate the pricing and token count for AWS Bedrock models.
        
        - Select the model type and enter the number of input and output tokens to calculate the estimated cost.
        - Paste your text in the Token Estimator to get an estimate of the token count.
        """)

if __name__ == "__main__":
    main()