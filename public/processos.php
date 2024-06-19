<?php

$nameArquivo = 'file';
$fileTempPath = $_FILES[$nameArquivo]['tmp_name'];
$fileName = $_FILES[$nameArquivo]['name'];
$fileType = $_FILES[$nameArquivo]['type'];

// Inicializar o cURL
$curl = curl_init();

// Configurações do cURL
curl_setopt_array($curl, array(
    CURLOPT_URL => 'http://0.0.0.0:8000/api/imagem/extracoes',
    CURLOPT_RETURNTRANSFER => true,
    CURLOPT_ENCODING => '',
    CURLOPT_MAXREDIRS => 10,
    CURLOPT_TIMEOUT => 0,
    CURLOPT_FOLLOWLOCATION => true,
    CURLOPT_HTTP_VERSION => CURL_HTTP_VERSION_1_1,
    CURLOPT_CUSTOMREQUEST => 'POST',
    CURLOPT_POSTFIELDS => ['file' => new CURLFILE($fileTempPath, $fileType, $fileName)],
));

// Executar e obter a resposta do cURL
$response = curl_exec($curl);

// Fechar a sessão cURL
curl_close($curl);

// Decodificar a resposta JSON em um array associativo
$data = json_decode($response, true);

// Inicializar arrays para armazenar os valores extraídos
$textAsHtmlArray = [];
$textArray = [];
$typeArray = [];
$elementIdArray = [];

// Iterar sobre cada elemento no array 'elements'
foreach ($data['elements'] as $element) {
    $typeArray[] = $element['type'];
    $elementIdArray[] = $element['element_id'];
    $textArray[] = $element['text'];
    
    // Verificar se 'metadata' e 'text_as_html' estão presentes
    if (isset($element['metadata']['text_as_html'])) {
        $textAsHtmlArray[] = $element['metadata']['text_as_html'];
    } else {
        $textAsHtmlArray[] = null; // ou outro valor padrão, se necessário
    }
}

// Exibir os valores armazenados
echo "Tipos:\n";
print_r($typeArray);

echo "Element IDs:\n";
print_r($elementIdArray);

echo "Textos:\n";
print_r($textArray);

echo "Textos como HTML:\n";
print_r($textAsHtmlArray);
