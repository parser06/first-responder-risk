//
//  ContentView.swift
//  FirstResponder Watch App
//
//  Created by Dennis Miczek on 9/13/25.
//

import SwiftUI

struct ContentView: View {
    var body: some View {
        VStack {
            Image(systemName: "bolt.heart.fill")
                .imageScale(.large)
                .foregroundStyle(.tint)
            Text("First Responder Monitor")
        }
        .padding()
    }
}

#Preview {
    ContentView()
}
