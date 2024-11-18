import re

text = """ChatCompletion(id='chatcmpl-AUxRvs041rJFGh1FgBNu5JxI5E2Lh', choices=[Choice(finish_reason='stop', index=0, logprobs=None, message=ChatCompletionMessage(content='1. 6000\n2. 3000', refusal=None, role='assistant', function_call=None, tool_calls=None))], created=1731941727, model='gpt-3.5-turbo-0125', object='chat.completion', service_tier=None, system_fingerprint=None, usage=CompletionUsage(completion_tokens=11, prompt_tokens=96, total_tokens=107, prompt_tokens_details={'cached_tokens': 0, 'audio_tokens': 0}, completion_tokens_details={'reasoning_tokens': 0, 'audio_tokens': 0, 'accepted_prediction_tokens': 0, 'rejected_prediction_tokens': 0}))"""

# Hitta innehåll inom 'content'
matches = re.findall(r"content='([^']*)'", text)
if matches:
    # Extrahera alla siffror från innehållet
    numbers = re.findall(r"\d+", matches[0])  # Leta efter alla siffror i 'content'
    # Filtrera bort 1 och 2
    numbers = [int(num) for num in numbers if num not in ["1", "2"]]
    print(numbers)
else:
    print("Hittade inget matchande innehåll.")
