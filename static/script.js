document.getElementById('questionForm').addEventListener('submit', async function (event) {
    event.preventDefault(); // Prevent form submission

    const question = document.getElementById('question').value;
    const responseDiv = document.getElementById('response');
    const answerParagraph = document.getElementById('answer');

    try {
        const response = await fetch('/query', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ question: question }),
        });

        const data = await response.json();

        if (response.ok) {
            // Clear previous content
            answerParagraph.innerHTML = '';

            if (Array.isArray(data.results)) {
                // Case 1: If the answer is an array, display each item as a list
                const parentDiv = document.createElement('div');
                parentDiv.className = 'list-answer-container';
                const ul = document.createElement('ul');
                data.results.forEach((item) => {
                    const li = document.createElement('li');
                    li.textContent = item;
                    ul.appendChild(li);
                });
                parentDiv.appendChild(ul);
                answerParagraph.appendChild(parentDiv);
            } else if (typeof data.results === 'object') {
                // Case 2: If the answer is a dictionary, display key-value pairs
                Object.entries(data.results).forEach(([key, value]) => {
                    if (typeof value === "string" || value instanceof String) {
                        // Directly display key:value for string values
                        const keyValueElement = document.createElement('p');
                        //keyValueElement.textContent = `${value}`;
                        formattedOutput = formatAnswer(value);
                        //keyValueElement.textContent = formatAnswer(value);
                        keyValueElement.innerHTML = formattedOutput.replace(/\n/g, '<br>');
                        answerParagraph.appendChild(keyValueElement);
                    }
                    else {
                        const parentDiv = document.createElement('div');
                        parentDiv.className = 'list-answer-container';
                        const keyElement = document.createElement('h3');
                        keyElement.textContent = key + ':';

                        const ul = document.createElement('ul');
                        
                        value.forEach((item) => {
                            const li = document.createElement('li');
                            li.textContent = item;
                            ul.appendChild(li);
                        });

                        parentDiv.appendChild(keyElement);
                        parentDiv.appendChild(ul);
                        answerParagraph.appendChild(parentDiv);
                        /*answerParagraph.appendChild(ul);*/
                    }   
                    
                });
            } else {
                // Case 3: If the answer is just a plain string
                answerParagraph.textContent = data.results || "No answer found.";
            }

            responseDiv.style.display = 'block';
        } else {
            answerParagraph.textContent = data.error || "An error occurred.";
            responseDiv.style.display = 'block';
        }
    } catch (error) {
        answerParagraph.textContent = "Failed to fetch the answer. Please try again.";
        responseDiv.style.display = 'block';
    }
});

function formatAnswer(inputText){
    // Replace \\n\\n with actual line breaks
    const formattedText = inputText.replace(/\\n\\n/g, '\n');

    // Extract the resource link and replace it with a clickable hyperlink
    const resourceRegex = /Resource:\s*(https?:\/\/[^\s]+)/;
    const match = formattedText.match(resourceRegex);

    if (match) {
        const url = match[1]; // Extracted URL
        const linkHtml = `<a href="${url}" target="_blank">Resource: ${url}</a>`;

        // Replace the "Resource:" line with the hyperlink
        return formattedText.replace(resourceRegex, linkHtml);
    }

    return formattedText;
}
