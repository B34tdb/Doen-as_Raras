import { Component, signal } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { TelaInicial } from './tela-inicial/tela-inicial';
import { Navbar } from './navbar/navbar';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, TelaInicial, Navbar],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App {
  protected readonly title = signal('doencaRara');
}
