import fs from 'fs';
import { program } from 'commander';

// Use dynamic import() to load the ES module
const loadConfig = async () => {
  const apptimusConfig = await import('./apptimus.config.js');
  return apptimusConfig.default; // Access the default export
};

// Main pull function to fetch languages and nodes, and process them
const pull = async () => {
  const apptimusConfig = await loadConfig(); // Load the config

  // Configurations from apptimus.config.js
  const type = apptimusConfig.wordbook.type || 'js'; // File type to be generated, defaults to 'js'
  const outDir = apptimusConfig.wordbook.outDir; // Output directory for the files
  const bookKey = apptimusConfig.wordbook.bookKey; // Book key used for API requests

  const apiUrl = apptimusConfig.nexus.apiUrl; // Base API URL
  const projectKey = apptimusConfig.nexus.projectKey; // Project key used for API requests

  // Remove the output directory if it exists to ensure a clean slate
  if (fs.existsSync(`${process.cwd()}/${outDir}`)) {
    fs.rmSync(`${process.cwd()}/${outDir}`, { recursive: true, force: true });
  }

  let languages = []; // Array to store fetched languages
  let nodes = []; // Array to store fetched nodes

  // Fetch languages from the API
  try {
    const languageResponse = await fetchLanguages(apiUrl, bookKey);
    if (languageResponse.is_success) {
      languages = languageResponse.result;
    } else {
      console.error('❌ ', 'Failed to fetch languages:', languageResponse.message || 'Unknown error');
      return;
    }
  } catch (error) {
    console.error('❌ ', 'An error occurred while fetching languages:', error.message);
    return;
  }

  // Create directories for each language
  languages.forEach((lang) => fs.mkdirSync(`${process.cwd()}/${outDir}/${lang.code}`, { recursive: true }));

  // Fetch nodes (files/folders) from the API
  try {
    const nodeResponse = await fetchNodes(apiUrl, bookKey);
    if (nodeResponse.is_success) {
      nodes = nodeResponse.result;
    } else {
      console.error('❌ ', 'Failed to fetch nodes:', nodeResponse.message || 'Unknown error');
      return;
    }
  } catch (error) {
    console.error('❌ ', 'An error occurred while fetching nodes:', error.message);
    return;
  }

  // Process nodes recursively for each language
  languages.forEach((lang) => {
    nodes.forEach((node) => processNode(lang, node, outDir, type, apiUrl, bookKey));
  });

  // Write the dictionary.js file
  writeDictionaryFile(languages, nodes, outDir, type);
};

// Recursive function to process each node (folder or file)
const processNode = async (lang, node, outDir, type, apiUrl, bookKey, parentPath = '') => {
  const currentPath = `${parentPath}/${node.name}`; // Current path for the node
  const fullPath = `${process.cwd()}/${outDir}/${lang.code}${currentPath}`; // Full path for the node

  if (node.type === 'folder') {
    // Create directory for the folder node
    fs.mkdirSync(fullPath, { recursive: true });
    if (node.children) {
      // Recursively process child nodes
      node.children.forEach((child) => processNode(lang, child, outDir, type, apiUrl, bookKey, currentPath));
    }
  } else if (node.type === 'file') {
    try {
      // Fetch strings for the file from the API
      const stringsResponse = await fetchStrings(apiUrl, bookKey, node.id, lang.id);
      if (stringsResponse.is_success) {
        // Convert strings to an object format for the output file
        const outputObject = stringsResponse.result.reduce((acc, curr) => {
          acc[curr.string] = curr.value;
          return acc;
        }, {});

        const objectString = JSON.stringify(outputObject, null, 2).replace(/"([^"]+)":/g, '$1:');

        // Write the object to the output file
        fs.writeFileSync(`${fullPath}.${type}`, `const ${node.name} = ${objectString};\n\nexport default ${node.name};`);

        console.log(`✔️  Successfully wrote strings for '${node.name}' in '${lang.code}'`);
      } else {
        console.error('❌ ', 'Failed to fetch strings for file:', node.name, stringsResponse.message || 'Unknown error');
      }
    } catch (error) {
      console.error('❌ ', 'An error occurred while fetching strings for file:', node.name, error.message);
    }
  }
};

// Function to fetch languages from the API
const fetchLanguages = async (apiUrl, bookKey) => {
  const response = await fetch(`${apiUrl}/wordbook-api/npm/${bookKey}/languages`, { method: 'GET' });
  return await response.json();
};

// Function to fetch nodes (files/folders) from the API
const fetchNodes = async (apiUrl, bookKey) => {
  const response = await fetch(`${apiUrl}/wordbook-api/npm/${bookKey}/nodes`, { method: 'GET' });
  return await response.json();
};

// Function to fetch strings for a specific file and language
const fetchStrings = async (apiUrl, bookKey, fileId, langId) => {
  const response = await fetch(`${apiUrl}/wordbook-api/npm/${bookKey}/strings?file_id=${fileId}&lang_id=${langId}`, {
    method: 'GET',
  });
  return await response.json();
};

// Function to write the dictionary.js file
const writeDictionaryFile = (languages, nodes, outDir, type) => {
  const imports = [];
  const dictionaryEntries = [];

  const processNodeForDictionary = (lang, node, parentPath = '') => {
    const currentPath = `${parentPath}/${node.name}`;
    if (node.type === 'file') {
      const importName = `${lang.code}${currentPath.replace(/\//g, '')}`;
      imports.push(`import ${importName} from "./${lang.code}${currentPath}";`);
      dictionaryEntries.push(`'${lang.code}${currentPath.replace(/\//g, '.')}': ${importName}`);
    } else if (node.type === 'folder' && node.children) {
      node.children.forEach((child) => processNodeForDictionary(lang, child, currentPath));
    }
  };

  languages.forEach((lang) => {
    nodes.forEach((node) => processNodeForDictionary(lang, node));
  });

  const importStatements = imports.join('\n');
  const dictionaryContent = `const dictionary ${type === 'ts' ? ': any' : ''} = {\n  ${dictionaryEntries.join(',\n  ')}\n};\n\nexport default dictionary;`;

  const fileContent =
    `// This file is generated by the CLI. Any changes made to this file will be overwritten.\n` + `// Please do not modify this file manually.\n\n${importStatements}\n\n${dictionaryContent}`;

  fs.writeFileSync(`${process.cwd()}/${outDir}/dictionary.${type}`, fileContent);
};

// Setting up the 'pull' command for the CLI using Commander
program
  .command('pull')
  .description('Pull language data from the database')
  .action(() => {
    pull();
  });

program.parse(process.argv); // Parse CLI arguments and execute the corresponding command
