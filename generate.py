import fire
import numpy as np
import torch
from transformers import GPT2LMHeadModel, GPT2Tokenizer

MAX_LENGTH = int(100)  # Hardcoded max length to avoid infinite loop
model_class = GPT2LMHeadModel
tokenizer_class = GPT2Tokenizer


def set_seed(args):
    np.random.seed(args.seed)
    torch.manual_seed(args.seed)
    if args.n_gpu > 0:
        torch.cuda.manual_seed_all(args.seed)


def adjust_length_to_model(length, max_sequence_length):
    if length < 0 and max_sequence_length > 0:
        length = max_sequence_length
    elif 0 < max_sequence_length < length:
        length = max_sequence_length  # No generation bigger than model size
    elif length < 0:
        length = MAX_LENGTH  # avoid infinite loop
    return length


def main(
    max_length=10_000,
    temperature=1,
    top_k=0,
    top_p=0.9,
    repetition_penalty=1.0,
    num_return_sequences=1,
    prompt_text="Your flavors are good, but your texture's all wrong.",
):
    # Initialize the model and tokenizer
    tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
    model = GPT2LMHeadModel.from_pretrained("gpt2")
    # model.to(args.device)
    encoded_prompt = tokenizer.encode(
        prompt_text, add_special_tokens=False, return_tensors="pt"
    )
    # encoded_prompt = encoded_prompt.to(args.device)
    if encoded_prompt.size()[-1] == 0:
        input_ids = None
    else:
        input_ids = encoded_prompt
    max_length += len(encoded_prompt[0])
    output_sequences = model.generate(
        input_ids=input_ids,
        max_length=max_length,
        temperature=temperature,
        top_k=top_k,
        top_p=top_p,
        repetition_penalty=repetition_penalty,
        do_sample=True,
        num_return_sequences=num_return_sequences,
    )
    # Remove the batch dimension when returning multiple sequences
    if len(output_sequences.shape) > 2:
        output_sequences.squeeze_()
    generated_sequences = []
    for generated_sequence_idx, generated_sequence in enumerate(output_sequences):
        print("=== GENERATED SEQUENCE {} ===".format(generated_sequence_idx + 1))
        generated_sequence = generated_sequence.tolist()
        # Decode text
        text = tokenizer.decode(generated_sequence, clean_up_tokenization_spaces=True)
        # # Remove all text after the stop token
        # text = text[: text.find(args.stop_token) if args.stop_token else None]
        # Add the prompt at the beginning of the sequence. Remove the excess text that was used for pre-processing
        n = len(tokenizer.decode(encoded_prompt[0], clean_up_tokenization_spaces=True))
        total_sequence = prompt_text + text[n:]
        generated_sequences.append(total_sequence)
        print(total_sequence)
    return generated_sequences


if __name__ == "__main__":
    fire.Fire(main)
