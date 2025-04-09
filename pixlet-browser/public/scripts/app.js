document.addEventListener('DOMContentLoaded', () => {
    const greetingElement = document.createElement('h1');
    greetingElement.textContent = 'Welcome to Pixlet!';
    document.body.appendChild(greetingElement);

    const buttonElement = document.createElement('button');
    buttonElement.textContent = 'Click me!';
    document.body.appendChild(buttonElement);

    buttonElement.addEventListener('click', () => {
        alert('Hello! Thanks for visiting Pixlet.');
    });
});