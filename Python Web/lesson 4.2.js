function isEven(number) {
    return number % 2 === 0;
}

for (let i = 1; i <= 10; i++) {
    if (isEven(i)) {
        console.log(`Число ${i} — парне`);
    } else {
        console.log(`Число ${i} — непарне`);
    }
}