import { Component, signal } from '@angular/core';

@Component({
  selector: 'app-tela-inicial',
  standalone: true,
  imports: [],
  templateUrl: './tela-inicial.html',
  styleUrl: './tela-inicial.css'
})
export class TelaInicial {
  // Apenas um sinal simples para alternar o ícone de mostrar/ocultar senha visualmente
  mostrarSenha = signal(false);

  alternarSenha(): void {
    this.mostrarSenha.update(valor => !valor);
  }
}