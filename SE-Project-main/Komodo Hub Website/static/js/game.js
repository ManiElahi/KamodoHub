document.addEventListener('DOMContentLoaded', () => {
  const gridSize = 10;
  const words = ['TIGER', 'RHINO', 'EAGLE', 'MYNA', 'TARSIUS', 'MACAQUE'];
  let grid = [];
  let selectedCells = [];
  let foundWords = new Set();
  let isMouseDown = false;

  const wordGrid = document.getElementById('word-grid');
  const wordList = document.getElementById('words');
  const newGameButton = document.getElementById('new-game');
  const message = document.getElementById('message');

  function initializeGame() {
    grid = Array.from({ length: gridSize }, () => Array(gridSize).fill(''));
    foundWords.clear();
    selectedCells = [];
    message.textContent = '';

    placeWords();
    fillRandomLetters();
    renderGrid();
    renderWordList();
  }

  function placeWords() {
    words.forEach(word => {
      let placed = false;
      while (!placed) {
        const direction = [[0,1],[1,0],[1,1]][Math.floor(Math.random()*3)];
        const row = Math.floor(Math.random()*gridSize);
        const col = Math.floor(Math.random()*gridSize);
        if(canPlace(word,row,col,direction)) {
          for(let i=0;i<word.length;i++) {
            grid[row + i*direction[0]][col + i*direction[1]] = word[i];
          }
          placed=true;
        }
      }
    });
  }

  function canPlace(word,row,col,[dr,dc]){
    for(let i=0;i<word.length;i++){
      let r=row+dr*i, c=col+dc*i;
      if(r>=gridSize||c>=gridSize||(grid[r][c]&&grid[r][c]!==word[i]))return false;
    }
    return true;
  }

  function fillRandomLetters() {
    for (let r=0;r<gridSize;r++){
      for (let c=0;c<gridSize;c++){
        if(!grid[r][c]){
          grid[r][c]=String.fromCharCode(65+Math.floor(Math.random()*26));
        }
      }
    }
  }

  function renderGrid() {
    wordGrid.innerHTML = '';
    wordGrid.style.gridTemplateColumns = `repeat(${gridSize},40px)`;
    for (let r=0;r<gridSize;r++){
      for (let c=0;c<gridSize;c++){
        const cell = document.createElement('div');
        cell.className = 'cell';
        cell.dataset.row=r;
        cell.dataset.col=c;
        cell.textContent=grid[r][c];

        cell.addEventListener('mousedown', handleMouseDown);
        cell.addEventListener('mouseenter', handleMouseEnter);
        cell.addEventListener('mouseup', handleMouseUp);

        wordGrid.appendChild(cell);
      }
    }
    document.body.addEventListener('mouseup', () => { isMouseDown=false; });
  }

  function renderWordList() {
    wordList.innerHTML = words.map(w => `<li data-word="${w}">${w}</li>`).join('');
  }

  function handleMouseDown(e){
    clearSelection();
    isMouseDown=true;
    selectCell(e.target);
  }

  function handleMouseEnter(e){
    if(isMouseDown) selectCell(e.target);
  }

  function handleMouseUp(){
    isMouseDown=false;
    checkWord();
  }

  function selectCell(cell){
    if(cell.classList.contains('found')||cell.classList.contains('selected'))return;
    cell.classList.add('selected');
    selectedCells.push(cell);
  }

  function clearSelection(){
    selectedCells.forEach(c=>c.classList.remove('selected'));
    selectedCells=[];
  }

  function checkWord(){
    const selectedWord=selectedCells.map(c=>c.textContent).join('');
    const reversed=selectedWord.split('').reverse().join('');
    if(words.includes(selectedWord)&&!foundWords.has(selectedWord)){
      markFound(selectedWord);
    } else if(words.includes(reversed)&&!foundWords.has(reversed)){
      markFound(reversed);
    } else clearSelection();

    if(foundWords.size===words.length){
      message.textContent='🎉 Congratulations!';
      message.classList.add("show");
      updatePoints();  // 🔁 Call backend
    }
  }

  function markFound(word){
    selectedCells.forEach(c=>{
      c.classList.remove('selected');
      c.classList.add('found');
    });
    document.querySelector(`li[data-word="${word}"]`).classList.add('found');
    foundWords.add(word);
    selectedCells=[];
  }

  function updatePoints(){
    fetch("/update_points", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ points: 10 })
    })
    .then(res => res.json())
    .then(data => {
      message.textContent += ` You earned +${data.points} points!`;
    })
    .catch(err => {
      console.error("Point update failed:", err);
    });
  }

  newGameButton.addEventListener('click', initializeGame);
  initializeGame();
});
