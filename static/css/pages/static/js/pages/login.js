document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('form-verificacao');
    const pinInputs = document.querySelectorAll('.campo-pin');
    const tokenInput = document.getElementById('token-2fa');

    if (!form || pinInputs.length === 0) return;

    // Foco inicial no primeiro campo
    pinInputs[0].focus();

    // Valida e monta o token completo antes de submeter
    form.addEventListener('submit', (e) => {
        let token = '';
        pinInputs.forEach(input => token += input.value);
        tokenInput.value = token;

        if (token.length !== 6) {
            e.preventDefault();
            Swal.fire({
                text: 'Por favor, preencha os 6 dígitos do código.',
                confirmButtonColor: '#0070f3',
                confirmButtonText: 'OK'
            });
        }
    });

    pinInputs.forEach((input, index) => {
        // Digitação: aceita somente números e avança automaticamente
        input.addEventListener('input', () => {
            input.value = input.value.replace(/\D/g, '');
            if (input.value && index < pinInputs.length - 1) {
                pinInputs[index + 1].focus();
            }
        });

        // Backspace: limpa e retorna ao campo anterior
        input.addEventListener('keydown', (e) => {
            if (e.key === 'Backspace' && !input.value && index > 0) {
                pinInputs[index - 1].focus();
            }
        });

        // Colar: distribui os dígitos nos blocos
        input.addEventListener('paste', (e) => {
            e.preventDefault();
            const textoColado = (e.clipboardData || window.clipboardData).getData('text').trim();
            const apenasNumeros = textoColado.replace(/\D/g, '');

            if (apenasNumeros.length > 0) {
                apenasNumeros.split('').slice(0, pinInputs.length).forEach((digito, i) => {
                    pinInputs[i].value = digito;
                });
                const proximoFoco = Math.min(apenasNumeros.length, pinInputs.length - 1);
                pinInputs[proximoFoco].focus();
            }
        });
    });
});